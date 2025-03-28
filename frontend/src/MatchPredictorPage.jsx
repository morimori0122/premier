import React from "react";
import { useParams, useNavigate, useLocation } from "react-router-dom";
import MatchPredictor from "./MatchPredictor";
import { getFullName } from "./utils/nameUtils";

const MatchPredictorPage = () => {
  const { slug } = useParams();
  const navigate = useNavigate();
  const location = useLocation();
  const result = location.state?.result;

  const [homeSlug, awaySlug] = slug.split("-vs-");
  const home = getFullName(homeSlug.replace(/-/g, " "));
  const away = getFullName(awaySlug.replace(/-/g, " "));

  return (
    <div className="p-4 w-full max-w-screen-lg mx-auto space-y-4">
      <button
        onClick={() => navigate(-1)}
        className="text-blue-500 hover:underline"
      >
        ← Back to Schedule
      </button>

      {result === null ? (
        <MatchPredictor homeTeam={home} awayTeam={away} />
      ) : (
        <div className="bg-white p-6 rounded-xl shadow">
          <h2 className="text-lg font-bold mb-4">
            {home} (H) vs {away} (A)
          </h2>
          <p className="text-md">
            result: {" "}
            {result === "home_win"
              ? "Home win"
              : result === "draw"
              ? "Draw"
              : result === "away_win"
              ? "Away win"
              : "Unknown"}
          </p>
        </div>
      )}
    </div>
  );
};

export default MatchPredictorPage;