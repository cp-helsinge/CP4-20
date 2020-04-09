"""============================================================================

  Enumerate game object types

============================================================================"""

class ObjectType:
  NEUTRAL         = 'Neutral'                     # As in background and ornameltal objects
  CGO             = 'Computer generated opponent' # Computer generated opponent
  UNFREINDLY      = 'Unfreindly object'           # Player or player generated    
  PLAYER          = 'Player'                      # Player or player generated    
  FREINDLY        = 'Frendly object'              # Player or player generated    
  PLAYER_OPPONENT = 'Other player'                # Other player in multiplayer game