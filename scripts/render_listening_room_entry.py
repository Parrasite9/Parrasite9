"""Render the animated listening-room link. Requires Pillow."""
from pathlib import Path
import math
from PIL import Image, ImageDraw, ImageFont
ROOT=Path(__file__).resolve().parents[1]
FONT='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
REG='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
def font(size,bold=True): return ImageFont.truetype(FONT if bold else REG,size)
W,H=1200,332
base=Image.new('RGB',(W,H),'#20182b');d=ImageDraw.Draw(base)
d.rounded_rectangle((1,1,W-2,H-2),radius=23,fill='#d6f78b')
d.rounded_rectangle((2,266,W-3,H-3),radius=22,fill='#20182b')
d.rectangle((2,266,W-3,290),fill='#20182b')
d.text((46,23),'ISAIAH’S LISTENING ROOM  /  THE AUX IS YOURS',font=font(15),fill='#364127')
d.text((43,59),'ENTER THE',font=font(46),fill='#20182b')
d.text((40,108),'LISTENING ROOM',font=font(88),fill='#20182b',stroke_width=1)
d.text((46,218),'Pick a record. Flip the sleeve. Press play.',font=font(23,False),fill='#364127')
d.text((46,287),'THREE RECORDS. NO SKIPS.',font=font(17),fill='#c2a1e4')
d.text((755,287),'CLICK TO STEP INSIDE',font=font(17),fill='#d6f78b')
d.ellipse((1010,83,1156,229),fill='#20182b')
frames=[]
for frame in range(60):
 im=base.copy();d=ImageDraw.Draw(im);phase=2*math.pi*frame/60
 # A gliding arrow and moving equalizer add motion without flashing the headline.
 shift=round(6*math.sin(phase));x=1082+shift;y=156
 d.line((x-25,y,x+25,y),fill='#d6f78b',width=7)
 d.line((x+3,y-23,x+27,y,x+3,y+23),fill='#d6f78b',width=7)
 for j in range(7):
  height=round(7+20*(.5+.5*math.sin(phase*(2+j%3)+j*.7)))
  x=1091+j*8
  d.rounded_rectangle((x,313-height,x+4,313),radius=2,fill='#d6f78b')
 # Small orbiting dot brings the eye toward the entry arrow.
 angle=phase-math.pi/2
 cx=1083+83*math.cos(angle);cy=156+83*math.sin(angle)
 d.ellipse((cx-4,cy-4,cx+4,cy+4),fill='#20182b')
 frames.append(im)
palette=frames[0].quantize(colors=128)
frames=[f.quantize(palette=palette,dither=Image.Dither.NONE) for f in frames]
frames[0].save(ROOT/'assets/listening-room-entry.gif',save_all=True,append_images=frames[1:],duration=50,loop=0,optimize=True,disposal=1)
frames[0].convert('RGB').save(ROOT/'assets/listening-room-entry.png')
print('Rendered 60-frame entrance marquee.')
