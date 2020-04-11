"""============================================================================

  Player space ship

  parameters:
    boundery  : boundary of movement
    position  : Start position. (default to center of boundry)
    speed     : Optional

============================================================================"""
import pygame
from game_functions.gameobject import *
import config

fire_rate = 3

class Player(Gameobject):
  # Variables to store animations and sounds common to all Player object
  loaded = False
  sprite = None
  sprit_bomb = None
  sprit_shot = None
  sound_die = None
  sound_shoot = None

  # Initialize Player 
  def __init__(self, boundary = None, position = None, speed = 20):
    print("init Player")
    # Load animations and sounds first time this class is used
    if not Player.loaded:
      Player.size = (80,80)
      Player.sprite = Animation("d1a1_rocket2.png", (100,100), Player.size,23) # sprite map
      Player.sprite_dying = Animation("a1a1_rocket2_dying.png", (100,100), Player.size,10,1) # sprite map
      #Player.sound_shoot = self.Sound("photon_torpedo_nx01_launch.ogg")
      Player.sound_shoot = Sound("shot.ogg")
      Player.loaded = True # Indicate that all common external attributes are loaded

    # Inherit from game object class
    Gameobject.__init__(self, boundary, position, self.sprite.size, speed)
    self.fire_rate = fire_rate
    self.last_shot = 0

    # Set charakteristica other than default
    self.type = self.Type.PLAYER
    self.impact_power = 100

    # Make this object accessable to other objects
    self.game_state.player = self # !!!!!!!!!!

  # Draw on game surface
  def draw(self, surface):
    if self.inactive:
      # Show player to wreck sprite
      surface.blit(self.sprite_dying.get_surface(),self.rect)  

    # Show player
    else:      
      surface.blit(self.sprite.get_surface(),self.rect)
    
  # Movement
  def update(self, scroll):
    if scroll[0] or scroll[1]:
      self.boundary.move(scroll)
      self.rect.move(scroll)

    if not self.inactive:
      # Move player according to input
      if self.game_state.key['left']:
        self.direction = 180
        self.move()
      
      if self.game_state.key['right']:
        self.direction = 0
        self.move()
      
      if self.game_state.key['up']:
        self.direction = 90
        self.move()
      
      if self.game_state.key['down']:
        self.direction = 270
        self.move()
      
      # Fire, but only if  1 / fire_rate seconds has passed since last shot
      if self.game_state.key['fire'] and ( ( pygame.time.get_ticks() - self.last_shot ) > 1000 / self.fire_rate ):
        # Save stooting time
        self.sound_shoot.play()
        self.last_shot = pygame.time.get_ticks()
        self.game_state.game_objects.add({
          'class_name': 'ShotPhotonTorpedoNx01',
          'position': self.rect.midtop,
          'boundary': None,
          'speed': 5,
          'direction': 90
        })

  # When hit or hitting something
  def hit(self, obj):
    if obj.type == self.Type.CGO or obj.type == self.Type.UNFREINDLY:
      print("I was hit by",obj.type,obj.__class__.__name__,obj.impact_power)
      self.health -= max( obj.impact_power + self.armor, 0)

    if self.health <= 0:
      # Reset player death animation
      self.sprite_dying.frame_time = False
      self.inactive = True
      #self.delete = True


