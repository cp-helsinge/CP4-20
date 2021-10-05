#!/usr/bin/env python3 
# -*- coding: utf-8 -*-
"""============================================================================

  Alien Attack

  This purpose of this game setup, is to teach and demonstrate techniques, 
  for making applications and games in a collaborating team.

  The intention is to set up a framework, for building a game, in a relatively 
  short time, without the hassle of writing a game from scratch each time, 
  but maintaining a loose understanding of how things work.
  Originally designed for Coding Pirates - Helsinge Denmark, 
  By Simon Rigét 2019
  ----------------------------------------------------------------------------
  Requires pygame, Qt5, screeninfo, pickledb libraries to be installed.

  ----------------------------------------------------------------------------

  The game it self, is wrapped in a Qt application, with a few pages, for 
  managing the game and setup etc.
  ----------------------------------------------------------------------------

============================================================================"""
version = "CP4-20"

import sys
import os
import glob
from PyQt5 import uic, QtCore, QtWidgets, QtGui
import pygame

import game
import config
from game_functions import common, game_classes, highscore
from game_attributes import story

config.root_path     = os.path.join(os.path.dirname(__file__))       # Root of this package
config.qt_path       = os.path.join(config.root_path,'qt')           # root of QT application files
config.game_obj_path = os.path.join(config.root_path,'game_objects') # Game program objects
config.html_path     = os.path.join(config.root_path,'qt','html')    # QT HTML pages
config.gfx_path      = os.path.join(config.root_path,'gfx')          # Graphic art and sprites
config.sound_path    = os.path.join(config.root_path,'sound')        # sound effects and music

current_game = None # Global 

# Create a widget, using a HTML file (located in the html_path.
# The  widget can only interpret simple HTML. It uses a subset of HTML 3.2 and 4. And css 2.1
# External links wil be opned in the system browser, where as internal links wil be followed 
# in the document root directory (html_path)
# If you need a comprehensive HTML browser, use the QWebEngine module. 
class SimpleHTMLPage:
  def __init__(self, url):
    self.widget = QtWidgets.QTextBrowser()
    # Enable external links to be opened in the system browser
    self.widget.setOpenExternalLinks(True)
    # Load the HTML, markdown or text file
    self.widget.setSource(QtCore.QUrl().fromLocalFile(os.path.join(config.html_path,url)))

class MainPage():
  def __init__(self, navigate):
    # Load a UI resource file
    self.widget = uic.loadUi(os.path.join(config.qt_path,'main_page.ui'))
    self.widget.version.setText(version)
    # Attach action to buttons
    self.widget.credits_button.clicked.connect(lambda: navigate("credits_page"))
    self.widget.boring_button.clicked.connect(lambda: navigate("boring_page"))
    self.widget.play_button.clicked.connect(lambda: navigate("play"))
    self.widget.exit_button.clicked.connect(lambda: navigate("exit"))
    self.widget.highscore_button.clicked.connect(lambda: navigate("highscore"))
    if config.cheat_page:
      cheat_button = QtWidgets.QPushButton('π', self.widget)
      cheat_button.autoFillBackground = True
      cheat_button.setGeometry(830,650,30,30)
      cheat_button.setStyleSheet("QPushButton{background:transparent;color: #FFF; border : 0;font-family: sans-serif;};")
      cheat_button.clicked.connect(lambda: navigate("cheat_page"))

class HighScore():
  def __init__(self, navigate):
    # Load a UI resource file
    self.widget = uic.loadUi(os.path.join(config.qt_path,'highscore.ui'))
    self.widget.parent = self

    # Set machine default user name
    name = self.widget.new_highscore_dialog.findChild(QtWidgets.QLineEdit, 'name')
    name.setText(QtCore.QDir().home().dirName())
    
    # Add buttons (to enable event handling)
    buttonbox = self.widget.new_highscore_dialog.findChild(QtWidgets.QDialogButtonBox, 'new_highscore_dialog_buttons')
    __apply = buttonbox.addButton(QtWidgets.QDialogButtonBox.Apply)
    __apply.clicked.connect(self.__save_highscore)
    __apply.setAutoDefault(True)
    buttonbox.addButton(QtWidgets.QDialogButtonBox.Discard).clicked.connect(self.widget.new_highscore_dialog.hide )
    self.widget.new_highscore_dialog.hide()

    # High score lists
    self.highscore = highscore.Highscore(config.highscore_key)

    self.update()
  
  def __save_highscore(self):
    # register new score
    self.highscore.set( self.widget.new_highscore_dialog.findChild(QtWidgets.QLineEdit, 'name').text(), self.new_score)
    # Display the new list
    self.update()
    # Hide the dialog box  
    self.widget.new_highscore_dialog.hide()
  
  def update(self):
    # Global list
    self.widget.global_highscore.clear()
    place = 1
    for i in self.highscore.get_global():
      self.widget.global_highscore.addItem( '{place:<3} {score:<6} {name:<8}'.format(**i,place=place) )
      place+=1

    # Local list
    self.widget.local_highscore.clear()
    place = 1
    for i in self.highscore.get_local():
      self.widget.local_highscore.addItem(  '{place:<3} {score:<6} {name:<8}'.format( **i,place=place) )
      place+=1

  def set(self):
    global current_game
    self.new_score = current_game.score
    # Display new high score
    name_input = self.widget.new_highscore_dialog.findChild(QtWidgets.QLabel, 'message')
    name_input.setText("Your score: " + str(self.new_score ))
    # Display dialog box (It will disappear again when the user clicks a button)
    self.widget.new_highscore_dialog.show()
    name_input.setFocus()

class CheatPage():
  def __init__(self, navigate):
    self.navigate = navigate
    # Load a UI resource file
    self.widget = uic.loadUi(os.path.join(config.qt_path,'cheat_page.ui'))

    # Set maximum level
    self.widget.level.setMaximum(len(story.level)-1)
    self.widget.level.setValue(len(story.level)-1)

    # Make list of game object classes
    self.game_objects = game_classes.GameClasses()
    for name in self.game_objects.class_list:
      self.widget.game_object.addItem(name)
    self.widget.game_object.clicked.connect(self.game_object_clicked)

    # Attach action to buttons
    self.widget.go_button.clicked.connect(lambda: self.cheat())
    
  # Show a sing object
  def game_object_clicked(self):
    global current_game

    print("Vis single object",self.widget.game_object.currentItem().text())
    window.hide()
    current_game = game.Game()

    current_game.game_objects.add({'class_name': 'Background', 'color':  pygame.Color('darkblue')})
    # Set up invisible emeny, to prevent game over
    current_game.game_objects.add({'class_name': 'AlienAlvin1', 'delay':1000000000000000}) 
    current_game.game_objects.add({'class_name': 'Player','position': current_game.rect.midbottom})
    current_game.game_objects.add({'class_name': self.widget.game_object.currentItem().text()})
    current_game.loop()
    del current_game
    window.show()

  def cheat(self):
    global current_game
    level = self.widget.level.text()
    print("Start at", level, "Superhealth:", self.widget.super_health.isChecked())
    window.hide()
    current_game = game.Game()
    # Set game variables to start values.
    current_game.level_controle.set(self.widget.level.value())
    if self.widget.super_health.isChecked():
      current_game.player.health = 100000000000000000

    current_game.loop()
    window.show()
    self.navigate('highscore')
    highscore = window.stacked_widget.widget(window.page['highscore']).parent
    highscore.update()
    highscore.set()
    del current_game

class MainWindow(QtWidgets.QWidget):
  def __init__(self, *args, **kwargs):
    super(MainWindow, self).__init__(*args, **kwargs)

    # Set screen size
    self.resize(1000, 700)

    # Create window and let staged widged contain all the pages used.
    layout = QtWidgets.QHBoxLayout(self, spacing=0)
    layout.setContentsMargins(0, 0, 0, 0)
    self.stacked_widget = QtWidgets.QStackedWidget(self)
    layout.addWidget(self.stacked_widget)
    
    # Create a back button (on all other pages than manin page)
    self.back_button = QtWidgets.QPushButton(QtGui.QIcon('qt/back.png'),"",self)
    self.back_button.setGeometry(QtCore.QRect(20, 20, 100, 100))
    self.back_button.setIconSize(QtCore.QSize(150, 150))
    self.back_button.clicked.connect(lambda: self.navigate("main_page"))
    self.back_button.hide()

    # Create stack of pages
    self.page = {}
    self.page['main_page'] = self.stacked_widget.addWidget(MainPage(self.navigate).widget)
    self.page['credits_page'] = self.stacked_widget.addWidget(SimpleHTMLPage('credits.html').widget)
    self.page['boring_page'] = self.stacked_widget.addWidget(SimpleHTMLPage('boring.html').widget)
    self.page['cheat_page'] = self.stacked_widget.addWidget(CheatPage(self.navigate).widget)
    self.page['highscore'] = self.stacked_widget.addWidget(HighScore(self.navigate).widget)

    self.keyPressEvent = self.newOnkeyPressEvent
    self.show()

  # Handle key inputs
  def newOnkeyPressEvent(self,e):
    for page_name, stack_index in self.page.items():
      if stack_index == self.stacked_widget.currentIndex():
        if page_name == 'main_page':
          if e.key() == QtCore.Qt.Key_Escape:
            self.navigate('exit')
          if e.key() == QtCore.Qt.Key_Return:
            self.navigate('play')
        else:
          if e.key() == QtCore.Qt.Key_Escape:
             self.navigate('main_page')

  # Navigate
  def navigate(self, page_name):
    global current_game

    #Hide back button, on main page
    if page_name == 'main_page':
      self.back_button.hide()
    else:
      self.back_button.show()

    # Go to page
    if page_name in self.page:
      self.stacked_widget.setCurrentIndex(self.page[page_name])
      # Let simple HTML pages be reloaded to its homepage. (Might have followed a link) 
      if isinstance(self.stacked_widget.currentWidget(), QtWidgets.QTextBrowser):
        self.stacked_widget.currentWidget().home()
        self.stacked_widget.currentWidget().reload()

    # Exit
    elif page_name == 'exit':
      sys.exit(0)

    # Start game
    elif page_name == 'play':
      self.hide()
      current_game = game.Game()
      current_game.start()
      window.show()
      self.navigate('highscore')
      highscore = window.stacked_widget.widget(window.page['highscore']).parent
      highscore.update()
      highscore.set()
      del current_game

# Start application
app = QtWidgets.QApplication(sys.argv)
window = MainWindow()

config.window        = window
config.app           = app

app.exec_()


