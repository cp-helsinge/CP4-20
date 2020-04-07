"""============================================================================

  City

  parameters:
    boundery  : boundary of movement
    position  : Start position. (default to center of boundry)
    speed     : Optional
    direction : in degrees 0-359 counting counter clockwise and 0 = right (optional)

============================================================================"""
import pygame
from game_functions.gameobject import *

class City(Gameobject):
  # Variables to store animations and sounds common to all Shot object
  loaded = False
  sprite = None
  sound_shoot = None
  count = 0

  # Initialize Shot 
  def __init__(self, boundary = None, position = None, direction = 90, speed = 10):
    # Load animations and sounds first time this class is used
    if not City.loaded:
      City.sprite = Animation("city7.png",None,(80,80)) 
      City.loaded = True # Indicate that all common external attributes are loaded
      City.count += 1

    # Inherit from game object class
    Gameobject.__init__(self, boundary, position,self.sprite.size, speed, direction)
 
    # Set charakteristica other than default
    self.type = self.Type.FREINDLY
    self.impact_power = 10
    self.health = 10
    self.amor = 1

  def __del__(self):
    City.count -= 1

  # Draw on game surface
  def draw(self, surface):
    surface.blit(self.sprite.get_surface(City.count),self.rect)
    
  # Movement
  def update(self, scroll):
    pass

  # When hit or hitting something
  def hit(self, obj):
    if obj.type == self.Type.CG_OPPONENT:
      self.health -= max( obj.impact_power + self.armor, 0)

    if self.health <= 0:
      # Reset death animation
      # self.sprite_dying.frame_time = False
      # self.inactive = True
      self.delete = True 
      self.game_state.score -= 10