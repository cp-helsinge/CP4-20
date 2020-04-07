"""============================================================================

  Shot Photon Torpedo NX01

  parameters:
    boundery  : boundary of movement
    position  : Start position. (default to center of boundry)
    speed     : Optional
    direction : in degrees 0-359 counting counter clockwise and 0 = right (optional)

============================================================================"""
import pygame
from game_functions.gameobject import *

class ShotPhotonTorpedoNx01(Gameobject):
  # Variables to store animations and sounds common to all Shot object
  loaded = False
  sprite = None
  sprit_bomb = None
  sprit_shot = None
  sound_die = None
  sound_shoot = None
  count = 0

  # Initialize Shot 
  def __init__(self, boundary = None, position = None, direction = 90, speed = 10):
    # Load animations and sounds first time this class is used
    if not ShotPhotonTorpedoNx01.loaded:
      ShotPhotonTorpedoNx01.sprite = Animation("photon_torpedo_nx01.png",(128,128),(50,50)) 
      ShotPhotonTorpedoNx01.loaded = True # Indicate that all common external attributes are loaded
      ShotPhotonTorpedoNx01.count += 1

    # Inherit from game object class
    Gameobject.__init__(self, boundary, position,self.sprite.size, speed, direction)
    
    # Adjust position to be centered on top of position
    self.rect.midbottom = position

    # Set charakteristica other than default
    self.type = self.Type.FREINDLY
    self.impact_power = 10
    self.health = 1

  def __del__(self):
    ShotPhotonTorpedoNx01.count -= 1

  # Draw on game surface
  def draw(self, surface):
    surface.blit(self.sprite.get_surface(ShotPhotonTorpedoNx01.count),self.rect)
    
  # Movement
  def update(self, scroll):
    if scroll[0] or scroll[1]:
      self.rect.move(scroll)
      self.boundary.move(scroll)

    # test if out of boundary and deflect sprite by mirroring direction
    if self.touch_boundary():
      self.delete = True

    self.move()
    self.speed += 0.4

  # When hit or hitting something
  def hit(self, obj):
    if not obj.type == self.Type.PLAYER and not obj.type == self.Type.FREINDLY:
      self.delete = True
