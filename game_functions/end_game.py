"""============================================================================

    End game


============================================================================"""

import pygame
from game_functions import animation
import config

class EndGame:
  def __init__(self, game_state):
    self.game_state = game_state
    self.in_progress = False
    self.background_sprite = None
    self.text_sprite = None
    
  def set(self, completed = False):
    self.game_state.suspended = True
    self.game_state.game_over = True
    self.in_progress = True

    self.font = pygame.font.Font(None,100) 
    self.text_color = (128,20,0)
    self.idle_average = 1

    if completed:
      print("Game succesfully over")
      # Load animation
      self.background_sprite = animation.Animation("fireworks.png",(500,474),self.game_state.rect.size,10,-1) 
      self.background_sprite.rect.center = self.game_state.rect.center
      # Load text animation
      self.text_sprite = animation.Animation("game_over_ball.png",(600,300),None,10,1) 
      self.text_sprite.rect.center = self.game_state.rect.center

    else:  
      print("Game over")
      # Load text animation
      self.background_sprite = animation.Animation("game_over_failed.png",(180,200),self.game_state.rect.size,10,1) 
      self.background_sprite.rect.center = self.game_state.rect.center


  def draw(self, surface):
    if self.in_progress:
      if self.background_sprite is not None:
        surface.blit(self.background_sprite.get_surface(),self.background_sprite.rect)
      if self.text_sprite is not None:
        surface.blit(self.text_sprite.get_surface(),self.text_sprite.rect)
  
   
  def display(self, x, y, format_str, *arguments):
    str = format_str.format(*arguments)
    text = self.font.render(str, True, self.text_color)
    self.surface.blit( text, (x, y) )

  def blitRotateCenter(surf, sprite, topleft, angle):

    rotated_sprite = pygame.transform.rotate(sprite, angle)
    new_rect = rotated_sprite.get_rect(center = sprite.get_rect(topleft = topleft).center)

    surf.blit(rotated_sprite, new_rect.topleft)
