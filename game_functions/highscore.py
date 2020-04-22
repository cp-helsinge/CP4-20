"""============================================================================
  Highscore

  maintain a local and a global highscore list
  
  Access external key value store 

  By Simon Rigét @Paragi 2020

============================================================================"""
import requests
import json

list_length = 13

class Highscore:
  def __init__(self, key):
    self.url = 'https://paragi.dk/api/highscore.php'
    # Set service id to access key value store
    self.service_id = 'KDCTY9560F3E3563A6SERWERWEW875EVYVRI'
    # Set key, unique to this game
    self.key = key
    self.global_list = {}
    self.local_list = {}
    self.db_filename = 'qt/highscore.db'
      
  def get_global(self):
    # Get list from server
    response = requests.post(self.url, { 'service': self.service_id, 'key': self.key })

    # Process response
    if response.status_code == 200:
      self.global_list = response.json()
      #self.list.sort(key=lambda operator: operator['score'] , reverse = True)
    elif response.status_code == 404:
      return ['No global highscore service at ' + self.url]
    
    else:
      return ['Global highscore service is off-line']

    if isinstance(self.global_list,list):
      return self.global_list
    else:
      return ["--< None >--" ]


  def get_local(self):
    # Read local highscore list (Stored in JSON format)
    try:
      with open(self.db_filename) as json_file:
        self.local_list = json.load(json_file)
    except:
      self.local_list = []
      # Ćreate local list in file
      with open(self.db_filename,"w") as json_file:
        json.dump(self.local_list,json_file)

    if len(self.local_list) <= 0:
      self.local_list = []
      return [{'score':'', 'name':"--< None >--"}]

    return self.local_list

  def set(self, name, score): 
    global list_length

    # Save local highscore
    # Get the latest local list from file (or empty)
    self.get_local()

    # Find the length of the hidhscore list
    length = len(self.local_list)
    # New record
    if length < list_length or score >= self.local_list[length-1]['score']:
      print("New local highscore",score)
      # Append to local highscore list, at the top, so that old entries are pushed down
      self.local_list.insert(0,{'name':name, 'score':score})
      # Sort the list after score and trim it to maximum length
      self.local_list = sorted(self.local_list, key=lambda k : k['score'], reverse = True)[:list_length]
      # Store local list in file
      with open(self.db_filename,"w") as json_file:
        json.dump(self.local_list,json_file)

      # transfer all local record to global list (In case we were off-line)      

      # Find the length of the hidhscore list
      length = len(self.global_list)
      # Compare top of local list to bottom of global list
      if self.local_list[0]['score'] >= self.global_list[length-1]['score']:
        post = {
            'service': self.service_id,
            'key': self.key,
            'value': json.dumps({'name':name, 'score':score}),
        }
        print("posting",post['value'])
        requests.post(self.url, post)

      
      



          

