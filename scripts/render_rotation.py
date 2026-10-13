"""Regenerate README GIFs from the SVG artwork. Requires Chrome and Pillow."""
from pathlib import Path
from tempfile import TemporaryDirectory
import math
import re
import shutil
import subprocess
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
# Published tempo references (UGK uses the 156 BPM double-time count):
# https://songbpm.com/@j-cole/poor-thang-q6ok1
# https://songbpm.com/@lloyd/southside
# https://tunebat.com/Info/Int-l-Players-Anthem-I-Choose-You-UGK-Outkast/0DgY053iwPDydoRymeGVZX
BPMS = [92, 75, 156]
BEATS_PER_REVOLUTION = 8
FRAME_MS = 50

CHROME = shutil.which('google-chrome') or shutil.which('chromium')
if not CHROME:
    raise SystemExit('Chrome or Chromium is required.')

for track, source in enumerate(sorted((ROOT / 'assets').glob('rotation-*.svg'))):
    svg = source.read_text()
    bars = re.findall(r'<rect class="equalizer-bar"[^>]*/>', svg)
    assert len(bars) == 7
    svg = re.sub(r'<style>.*?</style>', '', svg, flags=re.S)
    svg = re.sub(r'<rect class="equalizer-bar"[^>]*/>', '', svg)
    svg = svg.replace('width="360" height="180"', 'width="720" height="360"', 1)
    with TemporaryDirectory() as tmp:
        base = Path(tmp) / 'base.svg'
        shot = Path(tmp) / 'base.png'
        base.write_text(svg)
        subprocess.run([CHROME, '--headless', '--no-sandbox', '--disable-gpu',
                        '--hide-scrollbars', '--force-device-scale-factor=1',
                        '--window-size=720,500', f'--screenshot={shot}', base.as_uri()],
                       check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        background = Image.open(shot).convert('RGB').crop((0, 0, 720, 360))
    # Replace fixed reflections with moving arcs and a label marker.
    background_draw = ImageDraw.Draw(background)
    background_draw.ellipse((84, 34, 376, 326), fill='#141019', outline='#50335e', width=2)
    for radius in (62, 53, 44):
        background_draw.ellipse(((115-radius)*2, (90-radius)*2,
                                 (115+radius)*2, (90+radius)*2), outline='#34233f', width=2)
    color = dict(re.findall(r'([\w-]+)="([^"]*)"', bars[0]))['fill']
    background_draw.ellipse((172, 122, 288, 238), fill=color)
    background_draw.ellipse((218, 168, 242, 192), fill='#20182b')
    bpm = BPMS[track]
    frame_count = round(BEATS_PER_REVOLUTION * 60_000 / bpm / FRAME_MS)
    frames = []
    for frame in range(frame_count):
        canvas = background.copy()
        draw = ImageDraw.Draw(canvas)
        angle = 360 * frame / frame_count
        draw.arc((90, 40, 370, 320), start=angle-135, end=angle-100,
                 fill='#796486', width=3)
        draw.arc((102, 52, 358, 308), start=angle+40, end=angle+74,
                 fill='#4c3a59', width=3)
        radians = math.radians(angle)
        marker_x = 230 + 38 * math.cos(radians)
        marker_y = 180 + 38 * math.sin(radians)
        draw.ellipse((marker_x-4, marker_y-4, marker_x+4, marker_y+4), fill='#20182b')
        for i, bar in enumerate(bars):
            attrs = dict(re.findall(r'([\w-]+)="([^"]*)"', bar))
            x, full_height = int(attrs['x']), int(attrs['height'])
            # Integer beat cycles keep the bars and rotating record seamless.
            phase = 2 * math.pi * ((8 + i % 3) * frame / frame_count + i * .19 + track * .27)
            scale = .22 + .78 * ((math.sin(phase) + 1) / 2)
            top = 110 - full_height * scale
            draw.rounded_rectangle((x * 2, round(top * 2), (x + 5) * 2, 220),
                                   radius=4, fill=attrs['fill'])
        frames.append(canvas)
    # Use one palette throughout the animation to avoid color flicker.
    palette = frames[0].quantize(colors=128)
    frames = [f.quantize(palette=palette, dither=Image.Dither.NONE) for f in frames]
    dest = source.with_name(source.stem + '-spinning.gif')
    frames[0].save(dest, save_all=True, append_images=frames[1:], duration=FRAME_MS,
                   loop=0, optimize=True, disposal=1)
    with Image.open(dest) as check:
        assert check.n_frames == frame_count and check.info['loop'] == 0
    print(f'{dest.name}: {bpm} BPM, {frame_count} frames, {frame_count * FRAME_MS / 1000:.2f}s/revolution, {dest.stat().st_size // 1024} KiB')
