import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

const SchedulePage = () => {
  const [matches, setMatches] = useState([]);
  const [matchday, setMatchday] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    fetch("http://localhost:8000/next_matches")
      .then(res => res.json())
      .then(data => {
        setMatches(data.matches);
        setMatchday(data.matchday);
      });
  }, []);

  const toSlug = (teamName) =>
  teamName.replace(/\s+/g, "-").replace(/&/g, "and");

  return (
    <div className="p-6 space-y-6">
      <h1 className="text-2xl font-bold">Matchday {matchday}</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {matches.map((match, index) => (
          <div
            key={index}
            className="p-4 bg-white rounded-xl shadow hover:bg-gray-100 cursor-pointer"
            onClick={() => {
              const slug = `${toSlug(match.home)}-vs-${toSlug(match.away)}`;
              navigate(`/match/${slug}`, { state: { result: match.result } });
            }}
          >
            <h2 className="text-lg font-semibold">
              {match.home} vs {match.away}
            </h2>
            <p className="text-sm text-gray-600">{new Date(match.date).toLocaleString()}</p>
            {match.result && (
              <p className="text-sm mt-1">
                結果: {match.result === "home_win"
                  ? "Home win"
                  : match.result === "draw"
                  ? "Draw"
                  : match.result === "away_win"
                  ? "Away win"
                  : "Unknown"}
              </p>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

export default SchedulePage;
