import json
from datetime import datetime, timezone
from collections import defaultdict

json_dir = "test/"
json_file = "oe-scale-only.json"
json_path = json_dir + json_file

with open(json_path) as user_file:
  parsed_json = json.load(user_file)

data = defaultdict(dict)
def translate():
  
  highest = {
  'weight' : len(parsed_json['weight']),
  'flows' : len(parsed_json['flows']),
  'pressures' : len(parsed_json['pressures']),
}
  elapsed = max(highest)

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
    
  fix_issues()
  
def fix_issues():
  
  # delete ending 0s in flow list
  count = 0
  for i in reversed(data['flow']['by_weight']):
    if float(i) == 0:
      count += 1
    if float(i) > 0:
      break
  data['flow']['by_weight'] = data['flow']['by_weight'][:-count]

# from Odyssey Json file
name = f"Argos {parsed_json['name']}"
date = parsed_json.get('date')
dt = datetime.strptime(date, "%Y-%m-%dT%H:%M:%S.%fZ")
date_long = dt.astimezone(timezone.utc).strftime("%a %b %d %H:%M:%S %Z %Y")
epoch = int(dt.timestamp())
roastery = f"{parsed_json.get('roastery')} {parsed_json.get('beans')}"
dosage = parsed_json.get('dosage', 'null')
grinder_brand = parsed_json.get('grindBrand', '')
grinder_model = parsed_json.get('grindModel', '')
grinder_setting = str(parsed_json.get('grindSetting', ''))
if grinder_setting == "None":
  grinder_setting = ""
drink_weight = parsed_json.get('highestScaleWeight')
brewtemp = parsed_json.get('brewTemp')


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
        "drink_weight": drink_weight
      },
    }
  }
}

if __name__ == "__main__":
  
  translate()

  visualizer =  profile | data
  
  with open(f"visualizer_{json_file}", "w") as file:
    file.write(json.dumps(visualizer, indent=2))
