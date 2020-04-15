"""============================================================================

  The basics of the program, is that eash object that is active
      - paint it self on the shadow screen
      - move it self
      - does something when coliding with other objects

  The main loop makes sure alle active objets paint, move and hit functions is 
    called, at the appropriate time, player input is acted upon, and that the 
    shadow screen is fliped at regular intervals.

  Game frame by Simon Rigét @ paragi 2019. License MIT


pygame mixer issue for linux

tried:

apt-get install python-pygame
sudo apt-get install libsdl1.2-dev libsdl-image1.2-dev libsdl-mixer1.2-dev libsdl-ttf2.0-dev
sudo sdl-config --cflags --libs

https://stackoverflow.com/questions/32533585/pygame-projects-wont-run-pygame-error-no-available-video-device

============================================================================"""
# Import python modules
import pygame
#from pygame.locals import *
import time
import os
import sys
import glob
import pprint
from collections import defaultdict
from game_functions import gameobject, game_classes
import screeninfo
import config

import os

# Import game classes
from game_functions import dashboard, player_input, level_controle, tech_screen, gameobject, end_game, object_types, common

game_name = 'Alien Attack CP-20'
game_speed = 1

class Game(player_input.PlayerInput):
  class Type(object_types.ObjectType):
    pass
    
  # Constructor
  def __init__(self):
    self.level = 1
    self.score = 0
    self.player = None
    self.frame_start = 0
    self.level_time = 0
    self.frame_rate = config.frame_rate
    self.game_speed = game_speed
    self.fullscreen = False
    self.game_over = False
    self.suspended = False

    # Set up game screen
    pygame.init()
    # Set up the screen to match window size
    #self.resize((config.screen_width,config.screen_height))
    self.maximise()

    # start sound interface
    if not pygame.mixer.get_init():
      try:
        pygame.mixer.init()
      except Exception as err:
        print("Error: Pygame Sound mixer failed to initialize",err)


    # Set up a canvas to paint the game on
    self.canvas = pygame.Surface((config.screen_width,config.screen_height))

    # Define the game screen area
    self.rect = pygame.Rect(0,0,config.screen_width,config.screen_height) 
    
    pygame.display.set_caption(game_name)
    pygame.mouse.set_visible(False)

    # in game objects
    self.game_objects = game_classes.GameClasses()

    # Create basic game interface
    self.dashboard = dashboard.Dashboard(self)

    # Add functionality
    self.tech_screen = tech_screen.TechScreen(self)
    self.level_controle = level_controle.LevelControle(self)
    self.end_game = end_game.EndGame(self)

    # Make game states globally available
    config.game_state = self

  # Destructor  
  def __del__(self):
    self.exit()

  def exit(self):
    if self.fullscreen:
      self.toggle_fullscreen()

    # Close the game window
    pygame.display.quit()
    pygame.quit()

  def resize(self, new_size=None):
    if new_size is None:
      size = [config.screen_width,config.screen_height]
    else:
      size = [new_size[0], new_size[1]]

    # Maintain aspect ratio
    aspect_ratio = config.screen_width / config.screen_height
    # Too wide
    if size[0] / size[1] > aspect_ratio:
      size[0] = int(size[1] * aspect_ratio)

    # Too tall
    elif size[0] / size[1] < aspect_ratio:    
      size[1] = int(size[0] / aspect_ratio)

    self.screen = pygame.display.set_mode(  size , pygame.RESIZABLE )  # RESIZABLE | SCALED | FULLSCREEN | HWSURFACE | DOUBLEBUF
    self.screen_width, self.screen_height = size
    print("Resizing to:", size)
    
  def maximise(self):
    # Pygame does not support this
    # pygame.display.Info() is rather useless. Use Marcin Kurczewski's screeninfo 

    # Find which monitor to use. Assume using the largest screen in physical size
    monitor_list = screeninfo.get_monitors()
    physical_size = 0
    for m in monitor_list:
      if physical_size < m.width_mm + m.height_mm:  
        physical_size = m.width_mm + m.height_mm  
        monitor = m

    # Reduce size to allow for top bar etc.
    # Guess the size. 5% ?
    size = [int(monitor.width * 0.94), int(monitor.height * 0.94)]
    #size = [config.screen_width,config.screen_height]
    # Maintain aspect ratio
    aspect_ratio = config.screen_width / config.screen_height

    # Too wide
    if size[0] / size[1] > aspect_ratio:
      size[0] = int(size[1] * aspect_ratio)

    # Too tall
    elif size[0] / size[1] < aspect_ratio:    
      size[1] = int(size[0] / aspect_ratio)

    self.screen = pygame.display.set_mode(  size , pygame.RESIZABLE )  # RESIZABLE | SCALED | FULLSCREEN | HWSURFACE | DOUBLEBUF
    self.screen_width, self.screen_height = size  
    print("Maximising to:", size)

  def toggle_fullscreen(self):
    self.fullscreen = not self.fullscreen
    if self.fullscreen : 
      self.maximise()
      return
      # === Not working properly 
      if pygame.display.get_driver()=='x11c':
        pygame.display.toggle_fullscreen()
      else:
        self.screen = pygame.display.set_mode( (0, 0), pygame.FULLSCREEN )
      self.screen_width, self.screen_height = self.screen.get_size()
    else:  
      self.resize()
    print("Full screen:", self.fullscreen, pygame.display.get_driver())
    

  # test if a game object is active and hitable
  def __obj_active(self, obj):
    return not getattr( obj, 'delete', False) and not getattr( obj, 'dead', False) and getattr(obj, 'rect', False) 

  def start(self):
    # Set game variables to start values.
    self.game_over = False
    self.suspended = False
    self.level_controle.set(1)
    self.loop()

  # This is the main game loop
  def loop(self):
    self.maximise()
    self.reset_player_input()

    # Play music  
    try:
      pygame.mixer.music.play(-1)
    except Exception as err:
      print("Music playback failed:", err)  

    # Start using pygame loop timing (Frame rate)
    self.clock = pygame.time.Clock()
    while not self.stop:

      # Store the time that this frame starts
      self.frame_start = pygame.time.get_ticks()
  
      # Get player input
      self.update_player_input()

      #if type(self.background.sprite) is animation.Animate:
      #  self.canvas.blit(self.background.surface())fill((0,0,70))
      #else  

      # == move all objects ==
      scroll = (0,1)

      for game_obj in self.game_objects.list:
        if callable(getattr(game_obj, 'update', None)):
          game_obj.update(scroll)

      if not self.suspended:
        # == Collission check ==
        # Loop through all active objects
        for pos, obj1 in enumerate(self.game_objects.list):
          # Skip objects that are not active game objects
          if obj1.delete or obj1.inactive or obj1.type == gameobject.Gameobject.Type.NEUTRAL or obj1.invisible : continue
          # Loop through the rest of the list 

          for i in range(pos+1, len(self.game_objects.list) ):
            obj2 = self.game_objects.list[i]
            # Skip objects that are not active game objects
            if obj2.delete or obj2.inactive or obj2.type == gameobject.Gameobject.Type.NEUTRAL or obj2.invisible: continue

            # Compare rectangles of objects
            if obj1.rect.colliderect(obj2.rect):
              # Tell 1st. object that it has been hit by a 2nd. object class
              if getattr(obj1, 'hit', False):
                obj1.hit(obj2)
              # Tell 2nd. object that it has been hit by a 1st. object class
              if getattr(obj2, 'hit', False):
                obj2.hit(obj1)

        # Count game objects
        self.count = defaultdict(int)
        for game_obj in self.game_objects.list:
          if game_obj.delete or ( game_obj.inactive and not game_obj.invisible): continue

          # Count number of ocurences of each Class
          self.count[game_obj.__class__.__name__] += 1 
          
          # Count Player
          if game_obj.type == self.Type.PLAYER:
            self.count['player_items'] += 1

          if game_obj.type == self.Type.CGO:
            self.count['alien_items'] += 1
        
        # Check for level end
        self.level_controle.check()
   
      # == Delete obsolite objects ==
      for game_obj in self.game_objects.list:
        # Remove deleted objects
        if getattr(game_obj, 'delete', False):
          self.game_objects.list.remove(game_obj)

      # == Paint on screen ==
      # Draw all game objects
      for game_obj in self.game_objects.list:
        # Draw objects
        if callable(getattr(game_obj, 'draw', None)):
          game_obj.draw(self.canvas)

      if self.suspended:
        # == Display level and end game graphics ==
        if self.game_over:  
          self.end_game.draw(self.canvas)
        else:
          self.level_controle.draw(self.canvas)
      
      # Draw tech screen
      if self.tech_screen_on:
        self.tech_screen.draw(self.canvas)
    
      # Draw basic game interface
      self.dashboard.draw(self.canvas)

      # scale and show the new frame on screen
      self.screen.blit(pygame.transform.scale(self.canvas, self.screen.get_size()),(0,0))
      pygame.display.flip() 

      # Calculate timing and wait until frame rate is right
      self.clock.tick( self.frame_rate * self.game_speed )

    #Pause music
    try:
      pygame.mixer.music.pause()
    except: pass

    self.exit()

    
 