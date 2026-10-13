"""Regenerate README GIFs from the SVG artwork. Requires Chrome and Pillow."""
from pathlib import Path
from tempfile import TemporaryDirectory
import io
import math
import re
import shutil
import subprocess
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
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
    frames = []
    for frame in range(60):
        canvas = background.copy()
        draw = ImageDraw.Draw(canvas)
        for i, bar in enumerate(bars):
            attrs = dict(re.findall(r'([\w-]+)="([^"]*)"', bar))
            x, full_height = int(attrs['x']), int(attrs['height'])
            # Integer cycles make the 3-second loop seamless; phases vary per bar/card.
            phase = 2 * math.pi * ((2 + i % 3) * frame / 60 + i * .19 + track * .27)
            scale = .22 + .78 * ((math.sin(phase) + 1) / 2)
            top = 110 - full_height * scale
            draw.rounded_rectangle((x * 2, round(top * 2), (x + 5) * 2, 220),
                                   radius=4, fill=attrs['fill'])
        frames.append(canvas)
    # Use one palette throughout the animation to avoid color flicker.
    palette = frames[0].quantize(colors=128)
    frames = [f.quantize(palette=palette, dither=Image.Dither.NONE) for f in frames]
    dest = source.with_suffix('.gif')
    frames[0].save(dest, save_all=True, append_images=frames[1:], duration=50,
                   loop=0, optimize=True, disposal=1)
    with Image.open(dest) as check:
        assert check.n_frames == 60 and check.info['loop'] == 0
    print(f'{dest.name}: 60 frames, {dest.stat().st_size // 1024} KiB')
