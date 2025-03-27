import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

function SchedulePage() {
  const [matches, setMatches] = useState([]);
  const navigate = useNavigate();

  useEffect(() => {
    fetch("http://127.0.0.1:8000/next_matches")
      .then(res => res.json())
      .then(data => {
        setMatches(data.matches); // ← すでに { home, away, date } 形式になっている
      });
  }, []);

  const toSlug = (teamName) =>
    teamName.replace(/\s+/g, "-").replace(/&/g, "and");

  return (
    <div className="bg-white p-4 rounded-xl shadow mb-6">
      <h2 className="text-xl font-semibold mb-4">Upcoming Matches</h2>
      <ul>
        {matches.map((match, idx) => (
          <li
            key={idx}
            className="mb-2 p-3 border rounded-lg hover:bg-blue-100 cursor-pointer"
            onClick={() => {
              const slug = `${toSlug(match.home)}-vs-${toSlug(match.away)}`;
              navigate(`/match/${slug}`);
            }}
          >
            <span className="font-semibold">{match.home} (H)</span> vs{" "}
            <span className="font-semibold">{match.away} (A)</span>{" "}
            <span className="text-sm text-gray-500">
              ({new Date(match.date).toLocaleString()})
            </span>
          </li>
        ))}
      </ul>
    </div>
  );
}

export default SchedulePage;
