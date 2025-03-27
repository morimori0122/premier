import requests

API_TOKEN = '249ddafcaa4445c689485f40f4667a66'
headers = {'X-Auth-Token': API_TOKEN}
url = 'https://api.football-data.org/v4/competitions/PL/matches?status=SCHEDULED'

response = requests.get(url, headers=headers)
data = response.json()

# 次の試合日程を表示
for match in data['matches']:
    print(f"{match['homeTeam']['name']} vs {match['awayTeam']['name']} on {match['utcDate']}")
