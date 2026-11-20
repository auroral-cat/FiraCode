#! /usr/bin/env python3
from fontTools.misc.bezierTools import cubicPointAtT, solveQuadratic, splitCubicAtT
from ufo2ft.filters import BaseFilter, BaseIFilter

# A ufo2ft filter that puts a point at the leftmost, rightmost, topmost and bottommost spot
# of every curve, by splitting the curve there, which leaves its shape alone. For a variable
# font ufo2ft hands it the same glyph from every master at once, and all of them are split
# alike (so a master's point can sit a little off its own extreme)

def turns(p0, p1, p2, p3, axis):
  a, b, c, d = p0[axis], p1[axis], p2[axis], p3[axis]
  found = []
  # where the cubic's derivative, divided by 3, is zero
  for t in solveQuadratic(-a + 3 * b - 3 * c + d, 2 * (a - 2 * b + c), b - a):
    if 0 < t < 1:
      at = cubicPointAtT(p0, p1, p2, p3, t)[axis]
      # within half a unit of an end, the end is the extreme once points are rounded
      if at > max(a, d) + 0.5 or at < min(a, d) - 0.5:
        found.append(t)
  return sorted(found)

def split_points(segments):
  ts = []
  for axis in (0, 1):
    found = [turns(*segment, axis) for segment in segments]
    most = max(found, key=len)
    matched = []
    for here in found:
      if len(here) == len(most):
        matched.append(here)
        continue
      # a master whose curve turns fewer times takes the others' place for the missing turn
      filled = list(most)
      for t in here:
        filled[min(range(len(most)), key=lambda i: abs(most[i] - t))] = t
      matched.append(filled)
    # every master is split at the same place, so they still blend into the same curves
    ts += [sum(column) / len(column) for column in zip(*matched)]
  return sorted(ts)

def segment(walk, i):
  return [(p.x, p.y) for p in (walk[i - 3], walk[i - 2], walk[i - 1], walk[i])]

def split_curve(walk, i, ts):
  if not ts:
    return [walk[i - 2], walk[i - 1], walk[i]]
  Point = type(walk[i])
  pieces = splitCubicAtT(*segment(walk, i), *ts)
  points = []
  for piece in pieces[:-1]:
    points += [Point(*piece[1]), Point(*piece[2]), Point(*piece[3], type='curve', smooth=True)]
  return points + [Point(*pieces[-1][1]), Point(*pieces[-1][2]), walk[i]]

def add_extremes(glyphs):
  changed = False
  for contours in zip(*(glyph.contours for glyph in glyphs)):
    points = contours[0].points
    # walk each contour so it ends on an on-curve point: then every curve's handles come before it
    last = max(i for i, point in enumerate(points) if point.type)
    walks = [contour.points[last + 1:] + contour.points[:last + 1] for contour in contours]
    results = [[] for _ in contours]
    for i, point in enumerate(walks[0]):
      if point.type == 'curve':
        ts = split_points([segment(walk, i) for walk in walks])
        for walk, result in zip(walks, results):
          result += split_curve(walk, i, ts)
        changed |= bool(ts)
      elif point.type:
        for walk, result in zip(walks, results):
          result.append(walk[i])
    # start where the contour started, at its first on-curve point less the handles before it
    first = next(i for i, point in enumerate(points) if point.type)
    for contour, result in zip(contours, results):
      start = next(i for i, point in enumerate(result) if point is contour.points[first]) - first
      contour.points[:] = result[start:] + result[:start]
  return changed

class AddExtremesFilter(BaseFilter):
  def filter(self, glyph):
    return add_extremes([glyph])

class AddExtremesIFilter(BaseIFilter):
  def filter(self, glyph_name, glyphs):
    return add_extremes(glyphs)
