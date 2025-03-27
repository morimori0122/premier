import React, { useEffect, useState } from "react";
import { Card, CardContent } from "./components/ui/card";
import { BarChart, Bar, XAxis, YAxis, Tooltip } from "recharts";

function MatchPredictor({ homeTeam, awayTeam }) {
  const [result, setResult] = useState(null);
  const [probs, setProbs] = useState(null);
  const [rankings, setRankings] = useState({ home: null, away: null });
  const [homeForm, setHomeForm] = useState([]);
  const [awayForm, setAwayForm] = useState([]);

  useEffect(() => {
    const fetchPrediction = async () => {
      const featureRes = await fetch(
        `http://127.0.0.1:8000/features?home=${homeTeam}&away=${awayTeam}`
      );
      const featureData = await featureRes.json();
      setHomeForm(featureData.home_form);
      setAwayForm(featureData.away_form);
      setRankings({ home: featureData.home_rank, away: featureData.away_rank });

      const res = await fetch("http://127.0.0.1:8000/predict", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ features: featureData.features }),
      });

      const data = await res.json();
      setResult(data.result);
      setProbs(data.probabilities);
    };

    fetchPrediction();
  }, [homeTeam, awayTeam]);

  const renderForm = (formArray) =>
    formArray.map((result, index) => (
      <span key={index} className={`mx-1 font-bold ${
        result === "W" ? "text-green-500" :
        result === "D" ? "text-yellow-500" :
        "text-red-500"
      }`}>
        {result}
      </span>
    ));

  if (!probs) return null;

  const total = probs.home_win + probs.draw + probs.away_win;
  const normalizedProbs = {
    home_win: probs.home_win / total,
    draw: probs.draw / total,
    away_win: probs.away_win / total,
  };

  return (
    <div className="bg-white p-6 rounded-xl shadow">
      <h2 className="text-lg font-bold mb-4">{homeTeam} (H) vs {awayTeam} (A)</h2>

      {rankings.home && rankings.away && (
        <div className="mb-4 text-sm text-gray-700">
          <p>Home team ranking: {rankings.home}</p>
          <p>Away team ranking: {rankings.away}</p>
        </div>
      )}

      {result !== null && (
        <Card className="mb-4">
          <CardContent className="pt-4">
            <h2 className="text-lg font-semibold mb-2">Prediction</h2>
            <p>
              Result: {result === 0 ? "Away win" : result === 1 ? "Draw" : "Home win"}
            </p>
            <div className="my-4">
              <BarChart
                key={`${homeTeam}-${awayTeam}`}
                layout="vertical"
                width={1300}
                height={50}
                data={[{ name: "Probability", ...normalizedProbs }]}
              >
                <Bar
                  dataKey="home_win"
                  stackId="a"
                  fill="#60a5fa"
                  animationBegin={0}
                  animationDuration={1000}
                  isAnimationActive={true}
                />
                <Bar dataKey="draw" stackId="a" fill="#fbbf24" isAnimationActive={true} animationDuration={1000}/>
                <Bar dataKey="away_win" stackId="a" fill="#f87171" isAnimationActive={true} animationDuration={1000}/>
                <XAxis type="number" hide />
                <YAxis type="category" dataKey="name" hide />
                <Tooltip />
              </BarChart>

              <div className="flex justify-between text-sm mt-1">
                <span>Home win: {(probs.home_win * 100).toFixed(1)}%</span>
                <span>Draw: {(probs.draw * 100).toFixed(1)}%</span>
                <span>Away win: {(probs.away_win * 100).toFixed(1)}%</span>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      <div className="text-sm text-gray-700">
        <p>Home form: {renderForm(homeForm)}</p>
        <p>Away form: {renderForm(awayForm)}</p>
      </div>
    </div>
  );
}

export default MatchPredictor;