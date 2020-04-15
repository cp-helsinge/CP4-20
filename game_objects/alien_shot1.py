"""============================================================================

  Shot

  parameters:
    boundery  : boundary of movement
    position  : Start position. (default to center of boundry)
    speed     : Optional
    direction : in degrees 0-359 counting counter clockwise and 0 = right (optional)

============================================================================"""
import pygame
from game_functions.gameobject import *

class AlienShot1(Gameobject):
  # Variables to store animations and sounds common to all Shot object
  loaded = False
  sprite = None
  sound_shoot = None
  count = 0

  # Initialize Shot 
  def __init__(self, boundary = None, position = None, direction = 270, speed = 15):
    # Load animations and sounds first time this class is used
    if not AlienShot1.loaded:
      AlienShot1.sprite = Animation("shot_alien1.png") 
      AlienShot1.loaded = True # Indicate that all common external attributes are loaded
      AlienShot1.count += 1

    # Inherit from game object class
    Gameobject.__init__(self, boundary, position,self.sprite.size, speed, direction)
    
    # Adjust position to be centered under position
    if position:
      self.rect.midtop = position
  
    # Set charakteristica other than default
    self.type = self.Type.UNFREINDLY
    self.impact_power = 10
    self.health = 1

  def __del__(self):
    AlienShot1.count -= 1

  # Draw on game surface
  def draw(self, surface):
    surface.blit(self.sprite.get_surface(AlienShot1.count),self.rect)
    
  # Movement
  def update(self, scroll):
    if scroll[0] or scroll[1]:
      self.rect.move(scroll)
      self.boundary.move(scroll)

    # test if out of boundary and deflect sprite by mirroring direction
    if self.touch_boundary():
      self.delete = True

    self.move()

  # When hit or hitting something
  def hit(self, obj):
    if not obj.type == self.Type.UNFREINDLY and not obj.type == self.Type.CGO:
      self.delete = True
