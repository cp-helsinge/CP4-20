"""============================================================================

  Alien 1: Alien space ship 
  By Alvin 2020

  parameters:
    boundery  : boundary of movement
    position  : Start position. (default to center of boundry)
    speed     : Optional
    direction : in degrees 0-359 counting counter clockwise and 0 = right (optional)

============================================================================"""
import pygame
import math
from game_functions.gameobject import *

class AlienAlvin1(Gameobject):
  # Variables to store animations and sounds common to all AlienAlvin1 object
  loaded = False
  sprite = None
  sprit_bomb = None
  sprit_shot = None
  sound_die = None
  sound_shoot = None
  count = 0

  # === Initialize AlienAlvin1 ===
  def __init__(self, boundary = None, position = None, direction = 0, speed = 1, delay = 0):
    print("init alien")
    # Load animations and sounds first time this class is used
    if not AlienAlvin1.loaded:
      # Run this the first time this class is used
      AlienAlvin1.size = (100,50)
      AlienAlvin1.sprite = self.Animation("ufo1-{index}.png", (100,50), AlienAlvin1.size) # Alien sprite map
      AlienAlvin1.loaded = True # Indicate that all common external attributes are loaded

    # Get a animation offset that animation of the same class, looks different
    self.animation_offset = AlienAlvin1.count
    AlienAlvin1.count += 1

    # Inherit from game object class
    Gameobject.__init__(self, boundary, position, self.sprite.size, speed, direction)

    # Set charakteristica other than default
    self.type = self.Type.CGO
    self.impact_power = 50

    # Delayed deployment
    self.delay = delay
   
    self.inactive = self.invisible = delay > 0

  # === Movement ===
  def update(self, scroll):
    if self.invisible: 
      # wait fro delay to activate
      if (pygame.time.get_ticks() - self.game_state.level_time) // 1000 > self.delay:
        self.inactive = self.invisible = False
      else:
        return

    if scroll[0] or scroll[1]:
      self.boundary.move(scroll)
      self.rect.move(scroll)

    # test if out of boundary and deflect sprite by mirroring direction
    if self.touch_boundary():
      self.mirror_direction()

    # Move in circles
    self.direction += 3
    # Move sprite according to speed and direction
    self.move()

    # Shoot at player at random interval
    if self.random_frequency(0.1):
      # Direct shot at player
      target = self.game_state.player.rect.center

      # Place shot under alien ship
      self.game_state.game_objects.add({
        'class_name': 'AlienShot1',
        'position': self.rect.midbottom,
        'boundary': None,
        'speed': 15,
        'direction': math.degrees(math.atan2( target[0] - self.rect.x, target[1] - self.rect.y )) -90
      })

  # === Draw on game surface ===
  def draw(self, surface):
    if self.invisible:
      return

    # Flip image when direction is left
    surface.blit(self.sprite.get_surface(self.animation_offset),self.rect)

    # Draw healt bar  
    if self.health > 0:
      pygame.draw.line(
        surface,
        (200-self.health, self.health * 2, 0),
        (self.rect.x, self.rect.y),
        (self.rect.x + self.rect.width * self.health / 100, self.rect.y)
        ,(3)
      )

  # === When hit or hitting something ===
  def hit(self, obj):
    if self.invisible:
      return 
    if obj.type == self.Type.PLAYER or obj.type == self.Type.FREINDLY:
      #print("Alien hit by",obj.__class__.__name__)
      self.health -= obj.impact_power

    # Check if i'm dead
    if self.health <=0:  
      self.delete = True
      self.game_state.score += 50
