"""============================================================================

Animation

Loads an animation series (or just a still) and creates a pygame surface for it.

Animations are a collection of images, displayed with a given frame rate.
The images can be separate files, named so that only index numbers differ, or
a single image, containing multible frames within

parameters:
  name:       name of image file to load. if the file name contains "{index}"
              it is replaced with an index number, starting with 0. 

* frame_size: the rectangle (width, height) of the first frame within the image.
              frames are then picked out, from left to right, top to bottom order

* size:       Images are scaled to size if specified and rect variable is set 
              to the given position.

* frame_rate: number of images shown pr. second. If omitted, it is assumed that
              the whole series of images represents 1 second of animation

* loop:       The number of loop to perform. 
                 0 = using first image in the series as a still image. 
                 1 = animating the series one time, and ends with the last one
                -1 = loop forever
                n > 1 = number of loops performed, ending with the last image.

* Angles      If the animation set contains the figure from differant angles of
              orientation, this number is greater than 1 (default)
              It is assumed that the angled images represent the figure from 
              angles between 0 and 90 degrees (Last set being 90 degree)
              anything in between, will be the nearest angle, rotated to fit.
              90 - 180 degrees is vertically fliped version.
              180 - 270 degrees is fliped both vertically and horisontal
              270 -360 degrees is fliped horisontaly



* = optional

This class can be used for images, that are not part of an animation. Just 
ommit the text "{index}" in the filename and the frame_size parameter.

============================================================================"""
import os
import math
import pygame
import config

class Animation:
  def __init__(
    self, 
    name, 
    frame_size = None, 
    size = None, 
    frame_rate = None, 
    loop = -1,
    angles = 1
    ):
    self.file_name = os.path.join(os.getcwd(),config.gfx_path, name)
    self.name = name
    self.frame_size = frame_size
    self.size = size
    self.frame_rate = frame_rate
    self.loop = loop
    self.angles = angles

    self.collection = []
    self.frames = 0
    self.animation_ended = None
    self.frame_time = False
    self.rect = None
    self.orientation = 0
      
    # Load multiple image files as frames 
    if "{index}" in name: 
      self.collection = self.__load_image_sequence(self.file_name)

    # Load a single image file 
    else:
      self.collection = self.__load_sprite_map(self.file_name)

    if len(self.collection):
      self.rect = self.collection[0].get_rect()


    # Set meta data
    self.frames = len(self.collection) // self.angles 
    if self.angles > self.frames: 
      self.angles = self.frames
    # Find degrees between frame sets
    self.angle_step = 90 // (self.angles) 


    if self.frames > 0:
      # Set animation size 
      if size is None:
        if frame_size is None:
          self.size = pygame.Rect(self.collection[0].get_rect()).size
          self.frame_size = self.size
        else:
          self.size = frame_size

      # Set default frame rate to all frames in one second   
      if frame_rate is None: 
        self.frame_rate = self.frames


    
  # return a pointer to the current surface frame of this animation
  def get_surface(self, offset=0):
    # if there is no image, return immediately½½½
    if len(self.collection) < 1: 
      return None

    # Find the image to return
    # Still image
    if self.loop == 0:
      surface_index = 0

    # Animation has ended
    elif self.animation_ended:
      surface_index = self.frames-1

    else:
      # Start animation 
      if not self.frame_time:
        self.frame_time = pygame.time.get_ticks()
        
      # select frames based on ( time - begin_time ) * frame_rate / frames
      frame_changes = int(offset + (pygame.time.get_ticks() - self.frame_time) * self.frame_rate / 1000)

      # Stop animation
      if self.loop > 0 and frame_changes / self.frames >= self.loop:
        self.animation_ended = True
        surface_index = self.frames-1

      # Animate
      else:
        surface_index = frame_changes % self.frames

    # Set orientation
    if not self.orientation == 0:
      # limit orientation within 0-360 degrees
      self.orientation = (self.orientation % 360 + 360) % 360
      # Determin which quadrant of the unity circle  (1=0-90, 2=90-180 ...)
      quadrant =  ( self.orientation // 90 ) +1 
      # Mirror orientation angle to 1st. quadrant
      rotate = self.orientation % 90
      if quadrant == 2 or quadrant == 4:
          rotate = 90 - rotate
      # Find the frame set that fits orientatin best 
      frame_set = int( rotate / self.angle_step + 0.5 )
      if frame_set >= self.angles:
        frame_set = self.angles -1
      surface_index += self.frames * frame_set // self.angles
      # Adjust rotation to frame_set
      rotate = rotate - self.angle_step * frame_set
      # Flip into quadrant 
      flip_y_axis = ( quadrant == 2 or quadrant == 3)
      flip_x_axis = ( quadrant == 3 or quadrant == 4)

      # transform image
      surface = pygame.transform.rotate(self.collection[surface_index], rotate)
      surface = pygame.transform.flip(surface, flip_y_axis, flip_x_axis)
      surface = pygame.transform.smoothscale(surface, self.rect.size)
      return surface

    return self.collection[surface_index]

  # Load one or multiple image files as frames
  def __load_image_sequence(self, name):
    frame_list = []
    index = 0
    done = False
    while not done:
      try:
        image = pygame.image.load(self.file_name.format(index = index)).convert_alpha()
        # Scale image to size
        if self.size is not None:
          image = pygame.transform.smoothscale(image, self.size)
        else:
          self.size = image.rect.size  
      except Exception as error:
        if index <= 0:
          print(error, "Image sequence not loaded. Using default image.")
          image = self.__default_image()
        done = True

      frame_list.append(image)
      index += 1

    return frame_list

  # Use image to split into frames (Sprite map)
  def __load_sprite_map(self, file_name):
    frame_list = []
    try:
      image = pygame.image.load(self.file_name).convert_alpha()

    # If failing to load image file, create a default image
    except Exception as error:
      print(error, "Image or sprite map not loaded. Using default image.")
      image = self.__default_image()

    rect = image.get_rect()
    if self.frame_size is None:
      cols = 1
      rows = 1
      self.frame_size = rect.size
    else:
      cols = rect.width // self.frame_size[0]
      rows = rect.height // self.frame_size[1]

    if self.size is None:
      self.size =  self.frame_size

    for row in range(rows):
      for col in range(cols):
        # Mark positions of frame in map
        x = self.frame_size[0] * col 
        y = self.frame_size[1] * row 

        # Create a surface to hold the clip and cut it out
        clip = pygame.Surface(self.frame_size, pygame.SRCALPHA)
        clip.blit(image, (0,0), pygame.Rect((x,y),self.frame_size))
        
        # Scale clip and append it to the frame list
        if self.size != self.frame_size:
          clip = pygame.transform.smoothscale(clip, self.size)
        frame_list.append(clip)

    return frame_list

  def __fit_text_to_length(self, text, color, pixels, font_face = None):
    # Make the font sligthly bigger than it needs to
    font = pygame.font.SysFont(font_face, pixels *3// len(text) ) 
    # Render to surface
    text_surface = font.render(text, True, color)
    # scale to fit 
    size = text_surface.get_size()
    size = ( pixels, int(size[1] * pixels / size[0]) )
    return pygame.transform.scale(text_surface, size)

  # Create an image, with a rectangle arround and a cross in it
  def __default_image(self):
    if self.frame_size is None:
      self.frame_size = (100,100)
    image = pygame.Surface(self.frame_size)
    pygame.draw.rect(image, (200,0,0), ((0, 0), self.frame_size), 2)
    pygame.draw.line(image, (200,0,0), (0,0) , self.frame_size, 2)
    pygame.draw.line(image, (200,0,0), (0,self.frame_size[1]) , (self.frame_size[0], 0), 2)

    text = self.__fit_text_to_length(self.name, (200,0,0), int( self.frame_size[0] / 1.1))
    text_rect = text.get_rect()
    text_rect.center = image.get_rect().center
    image.blit( text, text_rect )
    return image
  


