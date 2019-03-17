from collections import namedtuple
try:
  import pygame
except ImportError:
  pygame = None

__all__ = ['Vector2', 'Collision', 'Rectangle', 'World']

Vector2 = namedtuple('Vector2', 'x, y')
Collision = namedtuple('Collision', 'rect, distance, normal, touch, response')

class Rectangle:
  def __init__(self, x, y, w, h):
    self.x, self.y = x, y
    self.w, self.h = w, h

  @classmethod
  def from_pos_size(cls, pos, size):
    return Rectangle(pos[0], pos[1], size[0], size[1])

  def copy(self):
    return Rectangle(self.x, self.y, self.w, self.h)

  @property
  def pos(self):
    return Vector2(self.x, self.y)

  @pos.setter
  def pos(self, pos):
    self.x, self.y = pos

  @property
  def size(self):
    return (self.w, self.h)

  @size.setter
  def size(self, size):
    self.w, self.h = size

  if pygame is not None:
    @property
    def pygame_rect(self):
      return pygame.Rect(self.x, self.y, self.w, self.h)

  def collide_rect(self, other):
    return (
      self.x <= other.x + other.w and other.x <= self.x + self.w and
      self.y <= other.y + other.h and other.y <= self.y + self.h
    )

  colliderect = collide_rect

  def collide_point(self, x, y):
    return (
      x >= self.x and x <= self.x + self.w and
      y >= self.y and y <= self.y + self.h
    )

  collidepoint = collide_point

  def minkowski_diff(self, other):
    return Rectangle(
      self.x - other.x - other.w,
      self.y - other.y - other.h,
      self.w + other.w,
      self.h + other.h
    )

  def __repr__(self):
    return "Rectangle((%f, %f), (%f, %f))" % (self.x, self.y, self.w, self.h)


def minkowski_diff(r1, r2):
  return Rectangle(
    r1.x - r2.x - r2.w,
    r1.y - r2.y - r2.h, 
    r1.w + r2.w, 
    r1.h + r2.h
  )


def clip_line(rect, ox, oy, idx, idy):
  mintx = (rect.x - ox) * idx
  maxtx = (rect.x + rect.w - ox) * idx
  minty = (rect.y - oy) * idy
  maxty = (rect.y + rect.h - oy) * idy

  if maxtx < mintx:
    mintx, maxtx = maxtx, mintx
    normx = 1
  else:
    normx = -1
  if maxty < minty:
    minty, maxty = maxty, minty
    normy = 1
  else:
    normy = -1
  if mintx > minty:
    t = mintx
    normal = Vector2(normx, 0)
  else:
    t = minty
    normal = Vector2(0, normy)
  col = maxty >= mintx and maxtx >= minty and t >= 0 and t <= 1
  return (t, normal) if col else None
  

def block_response(world, origin, cols, target, filter):
  return cols[0].touch, []


def pass_response(world, origin, cols, target, filter):
  return target, cols[1:]


def slide_response(world, origin, cols, target, filter):
  col = cols[0]
  new_rect = Rectangle.from_pos_size(col.touch, origin.size)
  if col.normal.x != 0:
    new_target = Vector2(new_rect.x, target.y)
  elif col.normal.y != 0:
    new_target = Vector2(target.x, new_rect.y)
  else:
    raise AssertionError('Normal must be non-zero')
  return new_target, world.sweep(new_rect, new_target, filter)


def bounce_response(world, origin, cols, target, filter):
  col = cols[0]
  new_rect = Rectangle.from_pos_size(col.touch, origin.size)
  if col.normal.x != 0:
    new_target = Vector2(2 * col.touch.x - target.x, target.y)
  elif col.normal.y != 0:
    new_target = Vector2(target.x, 2 * col.touch.y - target.y)
  else:
    raise AssertionError('Normal must be non-zero')
  return new_target, world.sweep(new_rect, new_target, filter)


def return_response(world, origin, cols, target, filter):
  col = cols[0]
  new_rect = Rectangle.from_pos_size(col.touch, origin.size)
  new_target = Vector2(2 * col.touch.x - target.x, 2 * col.touch.y - target.y)
  return new_target, world.sweep(new_rect, new_target, filter)


class World:
  responses = {
    'block': block_response,
    'pass': pass_response,
    'slide': slide_response,
    'bounce': bounce_response,
    'return': return_response,
    'ignore': None
  }

  def __init__(self):
    self.rects = []

  def add(self, rect):
    self.rects.append(rect)

  def remove(self, rect):
    self.rects.remove(rect)

  def check_move(self, rect, target, filter):
    def filter_wrapper(other):
      if other != rect: return filter(rect, other)
      else: return None
    return self.resolve(rect, target, filter_wrapper)

  def sweep(self, origin, target, filter):
    bounds = Rectangle(
      min(origin.x, target.x),
      min(origin.y, target.y),
      abs(origin.x - target.x) + origin.w,
      abs(origin.y - target.y) + origin.h
    )
    dirx = target.x - origin.x
    diry = target.y - origin.y
    idx = -1.0 / dirx if dirx != 0 else float('inf')
    idy = -1.0 / diry if diry != 0 else float('inf')
    cols = []
    for other in self.rects:
      response = filter(other)
      if not response or response == 'ignore' or not bounds.colliderect(other):
        continue
      diff = origin.minkowski_diff(other)
      col = clip_line(diff, 0, 0, idx, idy)
      if col:
        t, n = col
        t -= 1e-10
        touch = Vector2(origin.x + dirx * t, origin.y + diry * t)
        cols.append(Collision(
          rect=other, distance=t, normal=n, touch=touch,
          response=response
        ))
    cols.sort(key=lambda x: x.distance)
    return cols

  def resolve(self, origin, target, filter):
    cols = self.sweep(origin, target, filter)
    resolved_cols = []
    while len(cols) > 0:
      col = cols[0]
      response_func = self.responses[col.response]
      resolved_cols.append(col)
      target, cols = response_func(self, origin, cols, target, filter)
    return target, resolved_cols

