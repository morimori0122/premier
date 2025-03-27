from fastapi import FastAPI, Request, Query
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import numpy as np
import json
import joblib
from tensorflow.keras.models import load_model

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# データ・モデルの読み込み
matches = pd.read_csv("epl_games.csv")
matches["date"] = pd.to_datetime(matches["date"])
model = load_model("nn_model.h5")
scaler = joblib.load("scaler.pkl")
columns = joblib.load("feature_columns.pkl")

# チーム略称マップ
name_map = {
    "Arsenal Football Club": "Arsenal",
    "Association Football Club Bournemouth": "Bournemouth",
    "Aston Villa Football Club": "Aston Villa",
    "Brentford Football Club": "Brentford",
    "Brighton and Hove Albion Football Club": "Brighton",
    "Chelsea Football Club": "Chelsea",
    "Crystal Palace Football Club": "Crystal Palace",
    "Everton Football Club": "Everton",
    "Fulham Football Club": "Fulham",
    "Ipswich Town Football Club": "Ipswich",
    "Leicester City Football Club": "Leicester",
    "Liverpool Football Club": "Liverpool",
    "Manchester City Football Club": "Manchester City",
    "Manchester United Football Club": "Manchester United",
    "Newcastle United Football Club": "Newcastle",
    "Nottingham Forest Football Club": "Nottingham Forest",
    "Southampton Football Club": "Southampton",
    "Tottenham Hotspur Football Club": "Tottenham",
    "West Ham United Football Club": "West Ham",
    "Wolverhampton Wanderers Football Club": "Wolves",
}


@app.get("/")
def root():
    return {
        "message": "プレミアリーグ勝敗予測APIへようこそ！ POST /predict で予測できます。"
    }


@app.get("/teams")
def get_teams():
    teams = [{"label": full, "value": name_map[full]} for full in name_map]
    return {"teams": teams}


def get_team_features(df, team, role="home", n=5):
    recent = (
        df[df[f"{role}_club_name"] == team].sort_values("date", ascending=False).head(n)
    )
    if recent.empty:
        return {
            "club_position": 10,
            "recent_win_rate": 0.5,
            "total_minutes": 800,
            "avg_minutes": 80.0,
        }
    wins = recent["result_label"].apply(
        lambda r: 1 if r == f"{role}_win" else (0.5 if r == "draw" else 0)
    )
    return {
        "club_position": int(recent[f"{role}_club_position"].iloc[0]),
        "recent_win_rate": wins.mean(),
        "total_minutes": 90 * n,
        "avg_minutes": 90.0,
    }


def compute_past_match_score(df, home, away, n=3):
    history = []
    for _, row in df.iterrows():
        if set([row["home_club_name"], row["away_club_name"]]) == set([home, away]):
            if row["result_label"] == "home_win":
                point = 3 if row["home_club_name"] == home else 0
            elif row["result_label"] == "draw":
                point = 1
            else:
                point = 3 if row["home_club_name"] == away else 0
            history.append(point)
    if not history:
        return 1.0
    return np.mean(history[-n:])


def get_team_form(df, team, role="home", n=5):
    recent = (
        df[df[f"{role}_club_name"] == team].sort_values("date", ascending=False).head(n)
    )
    form = []
    for _, row in recent.iterrows():
        if row["result_label"] == f"{role}_win":
            form.append("W")
        elif row["result_label"] == "draw":
            form.append("D")
        else:
            form.append("L")
    return form


def generate_features(home: str, away: str):
    season_matches = matches[matches["season"] == 2024]

    home_feat = get_team_features(season_matches, home, "home")
    away_feat = get_team_features(season_matches, away, "away")
    score = compute_past_match_score(season_matches, home, away)

    features = {
        "home_club_position": home_feat["club_position"],
        "away_club_position": away_feat["club_position"],
        "home_recent_win_rate": home_feat["recent_win_rate"],
        "away_recent_win_rate": away_feat["recent_win_rate"],
        "home_total_minutes": home_feat["total_minutes"],
        "away_total_minutes": away_feat["total_minutes"],
        "home_avg_minutes": home_feat["avg_minutes"],
        "away_avg_minutes": away_feat["avg_minutes"],
        "past_match_score": score,
        f"home_club_name_{home}": 1,
        f"away_club_name_{away}": 1,
    }

    home_form = get_team_form(season_matches, home, "home")
    away_form = get_team_form(season_matches, away, "away")

    return {
        "features": features,
        "home_rank": home_feat["club_position"],
        "away_rank": away_feat["club_position"],
        "home_form": home_form,
        "away_form": away_form,
    }


@app.get("/features")
def get_features(home: str = Query(...), away: str = Query(...)):
    return generate_features(home, away)


@app.post("/predict")
async def predict(request: Request):
    body = await request.json()
    features = body["features"]
    input_df = pd.DataFrame([features])
    for col in columns:
        if col not in input_df.columns:
            input_df[col] = 0
    input_df = input_df[columns]
    input_scaled = scaler.transform(input_df)
    probs = model.predict(input_scaled)[0]
    result = int(np.argmax(probs))
    return {
        "result": result,
        "probabilities": {
            "away_win": round(float(probs[0]), 4),
            "draw": round(float(probs[1]), 4),
            "home_win": round(float(probs[2]), 4),
        },
    }


@app.get("/next_matches")
def get_next_matches():
    with open("schedule.json", "r") as f:
        raw_schedule = json.load(f)

    # 逆マッピングを作成
    inverse_name_map = {v: k for k, v in name_map.items()}

    matches = []
    added = set()

    for team, info in raw_schedule.items():
        if info["home_or_away"] == "home":
            home_fc = inverse_name_map.get(team, team)
            away_fc = inverse_name_map.get(info["opponent"], info["opponent"])
            key = (home_fc, away_fc)
            if key not in added:
                added.add(key)
                matches.append({"home": home_fc, "away": away_fc, "date": info["date"]})

    return {"matches": matches}
