import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from tensorflow.keras.callbacks import EarlyStopping
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout
from tensorflow.keras.utils import to_categorical
from tensorflow.keras.optimizers import Adam
import pickle
from collections import deque
from collections import defaultdict


# データ読み込み
epl_games = pd.read_csv("./archive/games.csv")
# appearances.csv を読み込む
appearances = pd.read_csv("./archive/appearances.csv")

# プレミアリーグだけに絞る
epl_games = epl_games[epl_games["competition_id"] == "GB1"].copy()

def compute_past_match_result(df, n=3):
    history = defaultdict(list)
    results = []

    for _, row in df.iterrows():
        home = row["home_club_name"]
        away = row["away_club_name"]
        key = tuple(sorted([home, away]))  # 相手関係を一意にする

        # 過去の同カード対戦履歴を取得
        past = history[key]

        # 特徴量：過去n試合の勝ち点平均を入れる（勝ち=3, 引き分け=1, 負け=0）
        if len(past) == 0:
            results.append(1.0)  # 情報なし → 中立値
        else:
            # 過去n件を使って計算
            recent = past[-n:]
            points = []
            for result in recent:
                if result == "home_win":
                    points.append(3 if row["home_club_name"] == home else 0)
                elif result == "draw":
                    points.append(1)
                else:  # away_win
                    points.append(3 if row["home_club_name"] == away else 0)
            avg_point = sum(points) / len(points)
            results.append(avg_point)

        # 今の試合結果を履歴に追加
        history[key].append(row["result_label"])

    return results

# 勝敗ラベルの作成
def get_result(row):
    if row["home_club_goals"] > row["away_club_goals"]:
        return 1
    elif row["home_club_goals"] == row["away_club_goals"]:
        return 0
    else:
        return -1

epl_games["result"] = epl_games.apply(get_result, axis=1)

# 勝敗表現を文字列ラベルに変換
def label_result(row):
    if row["home_club_goals"] > row["away_club_goals"]:
        return "home_win"
    elif row["home_club_goals"] < row["away_club_goals"]:
        return "away_win"
    else:
        return "draw"

epl_games["result_label"] = epl_games.apply(label_result, axis=1)

# 日付をdatetime型に変換

epl_games["date"] = pd.to_datetime(epl_games["date"])
epl_games = epl_games.sort_values("date")

# 相手別の相関情報の効果をメモっておく
def compute_recent_win_rate(df, team_col, role, n=5):
    win_rate = []
    history = {}
    for _, row in df.iterrows():
        team = row[team_col]
        result = row["result_label"]
        if team not in history:
            history[team] = deque(maxlen=n)
        if (role == "home" and result == "home_win") or (role == "away" and result == "away_win"):
            history[team].append(1)
        elif result == "draw":
            history[team].append(0.5)
        else:
            history[team].append(0)
        rate = sum(history[team]) / len(history[team]) if history[team] else 0.5
        win_rate.append(rate)
    return win_rate

# 勝率を計算
epl_games["home_recent_win_rate"] = compute_recent_win_rate(epl_games, "home_club_name", "home", n=5)
epl_games["away_recent_win_rate"] = compute_recent_win_rate(epl_games, "away_club_name", "away", n=5)

# 順位情報の空欄を埋める
epl_games["home_club_position"] = epl_games["home_club_position"].fillna(epl_games["home_club_position"].median())
epl_games["away_club_position"] = epl_games["away_club_position"].fillna(epl_games["away_club_position"].median())

epl_games["past_match_score"] = compute_past_match_result(epl_games, n=3)

# まず games.csv から game_id と season の対応を取得
game_season = epl_games[["game_id", "season"]]

# appearances に season 情報を追加
appearances = pd.read_csv("./archive/appearances.csv")
appearances = appearances.merge(game_season, on="game_id", how="left")

# シーズン・試合・クラブごとに出場時間を合計
team_minutes = appearances.groupby(["season", "game_id", "player_club_id"])["minutes_played"].sum().reset_index()
team_minutes.columns = ["season", "game_id", "club_id", "total_minutes"]

# ホームチームとマージ
epl_games = epl_games.merge(
    team_minutes,
    how="left",
    left_on=["season", "game_id", "home_club_id"],
    right_on=["season", "game_id", "club_id"]
)
epl_games.rename(columns={"total_minutes": "home_total_minutes"}, inplace=True)
epl_games.drop(columns=["club_id"], inplace=True)  # ← これを追加！

# アウェイチームとマージ
epl_games = epl_games.merge(
    team_minutes,
    how="left",
    left_on=["season", "game_id", "away_club_id"],
    right_on=["season", "game_id", "club_id"]
)
epl_games.rename(columns={"total_minutes": "away_total_minutes"}, inplace=True)
epl_games.drop(columns=["club_id"], inplace=True)  # ← 同様にここでも

# ① 試合・チームごとの平均出場時間を計算
avg_minutes = appearances.groupby(["game_id", "player_club_id"])["minutes_played"].mean().reset_index()
avg_minutes.columns = ["game_id", "club_id", "avg_minutes"]

# ② ホームチームとマージ
epl_games = epl_games.merge(
    avg_minutes,
    how="left",
    left_on=["game_id", "home_club_id"],
    right_on=["game_id", "club_id"]
)
epl_games.rename(columns={"avg_minutes": "home_avg_minutes"}, inplace=True)

# ③ アウェイチームとマージ
epl_games = epl_games.merge(
    avg_minutes,
    how="left",
    left_on=["game_id", "away_club_id"],
    right_on=["game_id", "club_id"]
)
epl_games.rename(columns={"avg_minutes": "away_avg_minutes"}, inplace=True)

# 不要な club_id を削除
epl_games.drop(columns=["club_id_x", "club_id_y"], inplace=True)

# One-Hot Encodingに使う列を選択
X_raw = epl_games[[
    "home_club_name",
    "away_club_name",
    "home_club_position",
    "away_club_position",
    "home_club_formation",
    "away_club_formation",
    "home_recent_win_rate",
    "away_recent_win_rate",
    "home_total_minutes",   # ← 追加！
    "away_total_minutes",
    "home_avg_minutes",       # ←追加！
    "away_avg_minutes",
    "past_match_score"
]]

# 目的変数
y = epl_games["result"].map({-1: 0, 0: 1, 1: 2})

# One-Hot Encoding
X_encoded = pd.get_dummies(X_raw, columns=[
    "home_club_name",
    "away_club_name",
    "home_club_formation",
    "away_club_formation"
])

# NaN を埋める
X_encoded = X_encoded.fillna(0)

# スケーリング
from sklearn.preprocessing import MinMaxScaler
scaler = MinMaxScaler()
X_scaled = scaler.fit_transform(X_encoded)

# 学習/テストに分割
X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.1, random_state=42)

# 正解ラベルを one-hot に変換（0,1,2 → [1,0,0], [0,1,0], [0,0,1]）
y_cat_train = to_categorical(y_train, num_classes=3)
y_cat_test = to_categorical(y_test, num_classes=3)

model_nn = Sequential([
    Dense(128, activation='relu', input_shape=(X_train.shape[1],)),
    Dropout(0.3),
    Dense(64, activation='relu'),
    Dropout(0.3),
    Dense(32, activation='relu'),
    Dense(3, activation='softmax')
])

model_nn.compile(
    optimizer=Adam(learning_rate = 0.001),
    loss='categorical_crossentropy',
    metrics=['accuracy']
)

early_stopping = EarlyStopping(monitor='val_accuracy', patience=3, restore_best_weights=True)

model_nn.fit(
    X_train,
    y_cat_train,
    validation_data=(X_test, y_cat_test),
    epochs=40,
    batch_size=16,
    callbacks=[early_stopping],
    verbose=1
)

# モデルの保存 ←これを追加！
model_nn.save("nn_model.h5")
with open("scaler.pkl", "wb") as f:
    pickle.dump(scaler, f)
# 特徴量の列名も保存（予測時に揃えるため）
with open("feature_columns.pkl", "wb") as f:
    pickle.dump(X_encoded.columns.tolist(), f)

epl_games.to_csv("epl_games.csv", index=False)

# 評価
loss, acc = model_nn.evaluate(X_test, y_cat_test, verbose=0)
print(f"NeuralNet Accuracy: {acc:.4f}")