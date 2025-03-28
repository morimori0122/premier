# Premier League Match Predictor

This app predicts match results of the Premier League (England) using a Machine Learning model.

- Backend: FastAPI
- Frontend: React + TailwindCSS + Recharts
- Model: Neural Network (TensorFlow + scikit-learn)
- Containerized with Docker
- CI: GitHub Actions (Lint / Build)

## Features

- Display upcoming Premier League matches
- Predict match outcomes with probabilities:
  - Home win / Draw / Away win
- Display predictions with bar charts
- Completed matches show actual result
- Automatically updates to the next matchweek

## How to Start

### 1. Clone the Repository

```bash
git clone https://github.com/morimori0122/premier.git
cd premier
```

### 2. Start with Docker

```bash
docker compose up --build
```

- Backend: http://localhost:8000  
- Frontend: http://localhost:3000

### 3. For Development

#### Frontend

```bash
cd frontend
npm install
npm run dev
```

#### Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn enhanced_ui_app:app --reload
```

## Project Structure

```
├── backend/           # FastAPI + ML model
├── frontend/          # React UI with TailwindCSS
├── docker-compose.yml
├── schedule.json      # Upcoming matches
├── NN_train.py        # Training script
```

## Data Source
https://www.kaggle.com/datasets/davidcariboo/player-scores

## Future Plans

- [ ] Add user predictions
- [ ] Supabase login integration
- [ ] Deploy to Render / Railway
- [ ] Save match logs and display results

## License

MIT

Built by [morimori0122](https://github.com/morimori0122)