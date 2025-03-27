// src/App.js
import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import SchedulePage from "./SchedulePage";
import MatchPredictorPage from "./MatchPredictorPage";

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gray-100 p-6">
        <h1 className="text-3xl font-bold mb-6 text-center text-blue-700">
          Premier League Match Predictor
        </h1>

        <Routes>
          <Route path="/" element={<SchedulePage />} />
          <Route path="/match/:slug" element={<MatchPredictorPage />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
