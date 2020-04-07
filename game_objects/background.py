
"""============================================================================

  Background

  Color or background

============================================================================"""
import pygame
from game_functions.gameobject import *

class Background(Gameobject):
  def __init__(self, file_name = None, color = None ):
    # Inherit from game object class
    Gameobject.__init__(self)

    # File name
    if type(file_name) is str:
      # Load animation 
      self.sprite = self.Animation(file_name,None,self.game_state.rect.size) 
      self.color = False

    # Background color
    elif color:
      self.color = color

    else:
      self.color = (0,0,70)  

    self.rect = self.game_state.rect

  def draw(self, surface):
    if self.color:
      surface.fill( self.color )
    else:
      surface.blit(self.sprite.get_surface(),self.rect)


