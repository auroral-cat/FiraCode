#! /usr/bin/env python3
import glyphsLib, sys
from ufo2ft.constants import FILTERS_KEY
from ufo2ft.filters.transformations import TransformationsFilter

# Turns a copy of FiraCode.glyphs into the source of its italic. Nothing is redrawn:
# the styles get italic names, and ufo2ft is asked to slant every glyph but line art
# while it compiles

ANGLE = 8 # degrees, around half the x-height

# line art that has to join up with its neighbours stays upright
UPRIGHT = [
  (0x2320, 0x2321), # integral pieces
  (0x239B, 0x23B3), # bracket, brace and summation pieces
  (0x23BA, 0x23BD), # scan lines
  (0x2500, 0x25FF), # box drawing, blocks, geometric shapes
  (0x2800, 0x28FF), # braille
  (0xE0A0, 0xE0D7), # powerline
  (0xEE00, 0xEE0B), # progress bar and spinner
  (0x1FB00, 0x1FBFF), # symbols for legacy computing
]

def is_upright(glyph):
  return any(lo <= int(u, 16) <= hi for u in glyph.unicodes for lo, hi in UPRIGHT)

def make_italic(path):
  font = glyphsLib.GSFont(path)
  upright = [glyph.name for glyph in font.glyphs if is_upright(glyph)]
  slant = {'name': 'transformations', 'pre': True, 'exclude': upright,
           'kwargs': {'Slant': ANGLE, 'Origin': TransformationsFilter.Origin.HALF_X_HEIGHT.value}}
  for master in font.masters:
    master.name += ' Italic' # the variable font is named after its masters
    master.italicAngle = ANGLE
    master.userData[FILTERS_KEY] = [slant]
  for instance in font.instances:
    instance.name = 'Italic' if instance.name == 'Regular' else instance.name + ' Italic'
    instance.isItalic = True
  font.save(path)
  print(f"make_italic: {ANGLE}° in {path}, {len(upright)} glyphs upright")

if __name__ == '__main__':
  make_italic(sys.argv[1])
  sys.exit(0)
