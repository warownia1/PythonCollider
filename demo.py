import collider
import pygame
from collider import Vector2, Rect
from itertools import chain
import timeit

pygame.init()
screen = pygame.display.set_mode((800, 600))
canv = pygame.Surface((800, 600), pygame.SRCALPHA)
collider.canv = canv
clock = pygame.time.Clock()

BLACK = pygame.Color(0, 0, 0, 255)
RED = pygame.Color(200, 0, 0, 255)
ORANGE = pygame.Color(200, 100, 0, 255)
LIME = pygame.Color(100, 200, 0, 255)
MAGENTA = pygame.Color(200, 0, 200, 255)
GREEN = pygame.Color(0, 200, 0, 255)
CYAN = pygame.Color(0, 200, 200, 255)
DARK_GREEN = pygame.Color(0, 80, 0, 255)
WHITE = pygame.Color(255, 255, 255, 255)
GRAY = pygame.Color(60, 60, 60, 255)


def pygame_rect(rect):
  return pygame.Rect(rect.x, rect.y, rect.w, rect.h)


block_rects = [Rect(20, y, 50, 50) for y in range(20, 200, 70)]
pass_rects = [Rect(90, y, 50, 50) for y in range(20, 200, 70)]
slide_rects = [Rect(160, y, 50, 50) for y in range(20, 200, 70)]
bounce_rects = [Rect(230, y, 50, 50) for y in range(20, 200, 70)]
return_rects = [Rect(300, y, 50, 50) for y in range(20, 200, 70)]
ignore_rects = [Rect(370, y, 50, 50) for y in range(20, 200, 70)]
all_rects = (
  block_rects + pass_rects + slide_rects + ignore_rects + bounce_rects +
  return_rects
)
world = collider.World()
world.rects.extend(all_rects)

selection = None
mouse = Vector2(0, 0)

def mouse_pressed(x, y, button):
  global selection
  if selection is None:
    for rect in all_rects:
      if rect.collidepoint(x, y):
        selection = rect
  else:
    xy, cols = world.check_move(selection, mouse, filter)
    selection.pos = xy
    selection = None

def mouse_moved(x, y):
  global mouse
  mouse = Vector2(x, y)


def filter(this, other):
  assert this == selection
  if other in block_rects: return 'block'
  elif other in pass_rects: return 'pass'
  elif other in slide_rects: return 'slide'
  elif other in bounce_rects: return 'bounce'
  elif other in return_rects: return 'return'
  elif other in ignore_rects: return 'ignore'
  else: return 'block'


run = True
while run:
  for event in pygame.event.get():
    if event.type == 12:
      run = False
    elif event.type == pygame.MOUSEBUTTONDOWN:
      mouse_pressed(event.pos[0], event.pos[1], event.button)
    elif event.type == pygame.MOUSEMOTION:
      mouse_moved(event.pos[0], event.pos[1])
  
  screen.fill((1, 1, 1, 255))
  canv.fill((0, 0, 0))
  for rect in pass_rects:
    pygame.draw.rect(canv, ORANGE, pygame_rect(rect))
  for rect in block_rects:
    pygame.draw.rect(canv, RED, pygame_rect(rect))
  for rect in slide_rects:
    pygame.draw.rect(canv, LIME, pygame_rect(rect))
  for rect in bounce_rects:
    pygame.draw.rect(canv, MAGENTA, pygame_rect(rect))
  for rect in return_rects:
    pygame.draw.rect(canv, CYAN, pygame_rect(rect))
  for rect in ignore_rects:
    pygame.draw.rect(canv, GRAY, pygame_rect(rect))
  if selection:
    xy, cols = world.check_move(selection, mouse, filter)
    ghost = selection.copy()
    for col in cols:
      ghost.pos = col.touch
      pygame.draw.rect(canv, DARK_GREEN, pygame_rect(ghost), 1)
    ghost.pos = mouse
    pygame.draw.rect(canv, WHITE, pygame_rect(ghost), 1)
    ghost.pos = xy
    pygame.draw.rect(canv, GREEN, pygame_rect(ghost), 1)
  
  screen.blit(canv, (0, 0))
  pygame.display.flip()
  clock.tick(30)

pygame.quit()