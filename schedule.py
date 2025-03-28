import requests
import json

API_TOKEN = '249ddafcaa4445c689485f40f4667a66'
headers = {'X-Auth-Token': API_TOKEN}
url = 'https://api.football-data.org/v4/competitions/PL/matches?status=SCHEDULED'

response = requests.get(url, headers=headers)
data = response.json()

schedule = []
for match in data['matches']:
    schedule.append({
        "matchday": match['matchday'],
        "date": match['utcDate'],
        "home": match['homeTeam']['name'],
        "away": match['awayTeam']['name'],
        "result": None
    })

# 日付順にソート（任意）
schedule.sort(key=lambda x: x['date'])

# JSONに保存
with open("backend/schedule.json", "w") as f:
    json.dump(schedule, f, indent=2)