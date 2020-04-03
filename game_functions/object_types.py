"""============================================================================

  Enumerate game object types

============================================================================"""

class ObjectType:
  NEUTRAL         = 'Neutral'                     # As in background and ornameltal objects
  CG_OPPONENT     = 'Computer generated opponent' # Computer generated opponent
  UNFREINDLY      = 'Opponent related object'     # Player or player generated    
  PLAYER          = 'Player object'               # Player or player generated    
  FREINDLY        = 'Player related object'       # Player or player generated    
  PLAYER_OPPONENT = 'Other player object'         # Other player in multiplayer game