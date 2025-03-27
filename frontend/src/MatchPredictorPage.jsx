import React from "react";
import { useParams, useNavigate } from "react-router-dom";
import MatchPredictor from "./MatchPredictor";
import { getFullName } from "./utils/nameUtils";

function MatchPredictorPage() {
  const { slug } = useParams(); // ← 修正ポイント

  const [home, away] = slug.split("-vs-").map((team) =>
    getFullName(team.replace(/-/g, " "))
  );

  const navigate = useNavigate();

  return (
    <div>
      <button
        className="text-blue-600 hover:underline mb-4"
        onClick={() => navigate(-1)}
      >
        ← Back to Schedule
      </button>

      <MatchPredictor homeTeam={home} awayTeam={away} />
    </div>
  );
}

export default MatchPredictorPage;
