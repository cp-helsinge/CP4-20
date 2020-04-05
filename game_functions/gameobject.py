"""============================================================================

  Game object template

  Inherited by all game objects

============================================================================"""
import pygame
import math
import random
import os
from game_functions import animation, object_types
import config

class Gameobject:
  class Type(object_types.ObjectType):
    pass
  
  class Animate(animation.Animation):
    def __init__(self, name, frame_size = None, size = None, frame_rate = None, loop = -1):
      animation.Animation.__init__(self, name, frame_size, size, frame_rate, loop)

  class Sound(pygame.mixer.Sound):
    # NB: mixer some times fail om linux
    def __init__(self, name):
      file_name = os.path.join(config.sound_path, name)
      try:
        pygame.mixer.Sound.__init__(self,file_name)
      except:
        print("Failed to load sound",file_name)
 
    # Make a dummy in case it failes
    def play(self):
      try:
        pygame.mixer.Sound.play(self)
      except: pass  

  def __init__(self, boundary = None, position=None, size=None, speed=1, direction=0):
    self.game_state = config.game_state

    self.speed      = speed
    self.direction  = direction

    if boundary:
      self.boundary   = pygame.Rect(boundary)
    else: 
      self.boundary = pygame.Rect((0,0), (config.screen_width, config.screen_height))
    #confine boundary to game area
    self.boundary = pygame.Rect.clip(self.boundary, self.game_state.rect)

    if not size:
      size = (100,100)

    if not position:
      position = self.boundary.center

    self.rect = pygame.Rect(position, size)

    self.inactive = False
    self.delete = False

    self.inventory = {}
    self.armor = 1
    self.health = 100
    self.impact_power = 100
    self.type = self.Type.NEUTRAL
    
  # Move object according to speed and direction, within boundary
  def move(self):
    radie = -math.radians(self.direction)
    x = self.speed * math.cos(radie)
    y = self.speed * math.sin(radie)
    new_rect = self.rect.move(x,y)
    new_rect.clamp_ip(self.boundary)
    self.rect = new_rect

  # Mirror direction, when hittinh boundary
  def mirror_direction(self):
    if self.touch_boundary():
      # Left and Right side
      if self.rect.x == self.boundary.x or self.rect.x + self.rect.width == self.boundary.x + self.boundary.width:       
        self.direction = -self.direction + 180
      
      # bottom  and top
      if self.rect.y == self.boundary.y or self.rect.y + self.rect.height == self.boundary.y + self.boundary.height:       
        self.direction = -self.direction 
      
      # reduce angle to 0-360 degrees
      self.direction = ((self.direction + 360 ) % 360) // 1  
      # Change to oposite direction

  def touch_boundary(self):
    touching = False
    touching |= self.rect.x <= self.boundary.x 
    touching |= self.rect.y <= self.boundary.y 
    touching |= self.rect.x + self.rect.width >= self.boundary.x + self.boundary.width 
    touching |= self.rect.y + self.rect.height >= self.boundary.y + self.boundary.height 
    return touching

  # Return true at random, on avarage at <freq> times pr. second
  def random_frequency(self, freq):
    return random.randint(0, config.frame_rate // freq ) == 0