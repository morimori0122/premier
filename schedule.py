from dotenv import load_dotenv
import os
import requests
import json

load_dotenv()
API_TOKEN = os.getenv("FOOTBALL_DATA_API_KEY")

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

schedule.sort(key=lambda x: x['date'])

with open("backend/schedule.json", "w") as f:
    json.dump(schedule, f, indent=2)