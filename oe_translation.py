import json
import requests
import getpass
from requests.auth import HTTPBasicAuth 
from datetime import datetime, timezone
from collections import defaultdict


def translate(parsed_json):
  data = defaultdict(dict)
  
  highest = {
  'weight' : len(parsed_json['weight']),
  'flows' : len(parsed_json['flows']),
  'pressures' : len(parsed_json['pressures']),
  }
  elapsed = max(highest, key=highest.get)

  # elapsed
  data['elapsed'] = []
  for i in parsed_json[elapsed]:
    data['elapsed'].append(str(i['x']))
    
  # weight
  data['totals']['weight'] = []
  for i in parsed_json['weight']:
    data['totals']['weight'].append(str(i['y']))

  # pressure
  data['pressure']['pressure'] = []
  for i in parsed_json['pressures']:
    data['pressure']['pressure'].append(str(i['y']))
    
  # flows
  data['flow']['by_weight'] = []
  for i in parsed_json['flows']:
    data['flow']['by_weight'].append(str(i['y']))
  
  # temp
  mult = len(parsed_json[elapsed])
  data['temperature']['goal'] = [parsed_json.get('brewTemp')] * mult
  
  # fix_issues(data)
  
  return data
  
def fix_issues(data):
  
  # delete ending 0s in flow list
  # not an issue with api upload
  count = 0
  for i in reversed(data['flow']['by_weight']):
    if count == 0 and float(i) > 0:
      break
    elif float(i) == 0:
      count += 1
    elif float(i) > 0:
      break
  if count != 0:
    data['flow']['by_weight'] = data['flow']['by_weight'][:-count]

def main(parsed_json):
  # from Odyssey Json file
  name = f"Argos {parsed_json['name']}"
  date = parsed_json.get('date')
  dt = datetime.strptime(date, "%Y-%m-%dT%H:%M:%S.%fZ")
  date_long = dt.astimezone(timezone.utc).strftime("%a %b %d %H:%M:%S %Z %Y")
  epoch = int(dt.timestamp())
  
  # # test
  # date = datetime.now()
  # date_long = date.astimezone(timezone.utc).strftime("%a %b %d %H:%M:%S %Z %Y")
  # epoch = int(datetime.now().timestamp())

  roastery = f"{parsed_json.get('roastery')} {parsed_json.get('beans')}"
  dosage = parsed_json.get('dosage', 'null')
  grinder_brand = parsed_json.get('grindBrand', '')
  grinder_model = parsed_json.get('grindModel', '')
  grinder_setting = str(parsed_json.get('grindSetting', ''))
  if grinder_setting == "None":
    grinder_setting = ""
  drink_weight = parsed_json.get('highestScaleWeight')
  bean_notes = parsed_json.get('flavorNotes')

  profile = {
    "clock" : str(epoch),
    "date" : str(date_long),
    "timestamp" : str(epoch),
    "profile" : {
      "title" : name,
    },
    "state_change": [],
    "app": {
      "data": {
        "settings": {
          "grinder_dose_weight": dosage,
          "grinder_setting": grinder_setting,
          "grinder_model": grinder_model,
          "bean_brand": roastery,
          "bean_type": "",
          "bean_notes": bean_notes,
          "drink_weight": drink_weight
        },
      }
    }
  }
  
  data = translate(parsed_json)
  
  visualizer =  profile | data
  
  return visualizer

def apiTest():
  with open('test/oe-scale-transducer.json') as f:
    parsed_json = json.load(f)
  translated_json = json.dumps(main(parsed_json))

  url = "https://visualizer.coffee/api/shots/upload"

  payload = translated_json
  headers = {
    'Content-Type': 'application/json'
  }

  username = input('Visualizer Email: ')
  while not username:
    username = input('Visualizer Email: ')
  password = getpass.getpass()
  while not password:
    password = getpass.getpass()
  
  response = requests.post(url, headers=headers, data=payload, auth=HTTPBasicAuth(username, password))
  
  if response.status_code == 200:
    print('Successfully posted shot')
    print(f'https://visualizer.coffee/shots/{response.json().get('id')}')
  else:
    print(f'Unsuccessful, Reason: {response.reason}')

if __name__ == "__main__":

  apiTest()