import { useState } from "react";
import PRInput from "./components/PRInput";
import ReviewFeed from "./components/ReviewFeed";
import useWebSocket from "./hooks/useWebSocket";

function App() {
  const [prId, setPrId] = useState(null);
  const [reviews, setReviews] = useState([]);
  const [done, setDone] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useWebSocket(prId, (message) => {
    if (message.done) {
      setDone(true);
      setLoading(false);
    } else {
      setReviews((prev) => [...prev, message]);
    }
  });

  const handleSubmit = async (url) => {
    setReviews([]);
    setDone(false);
    setError("");
    setLoading(true);

    try {
      const res = await fetch("http://localhost:8000/review", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "x-api-key": "randomly_generated_api_key"
        },
        body: JSON.stringify({ pr_url: url }),
      });
      const data = await res.json();

      if (data.error) {
        setError(data.error);
        setLoading(false);
        return;
      }

      setPrId(data.pr_id);
    } catch (e) {
      setError("Could not reach the backend. Is Docker running?");
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: 800, margin: "40px auto", fontFamily: "sans-serif", padding: "0 20px" }}>
      <h1>🔍 AI Code Review</h1>
      <PRInput onSubmit={handleSubmit} loading={loading} />
      {error && (
        <div style={{
          background: "#fef2f2", border: "1px solid #fca5a5",
          borderRadius: 8, padding: "12px 16px", marginBottom: 16, color: "#dc2626"
        }}>
          ⚠️ {error}
        </div>
      )}
      {loading && (
        <div style={{ color: "#6b7280", marginBottom: 16 }}>
          ⏳ Fetching diff and running AI review...
        </div>
      )}
      {done && (
        <div style={{
          background: "#f0fdf4", border: "1px solid #86efac",
          borderRadius: 8, padding: "12px 16px", marginBottom: 16, color: "#16a34a"
        }}>
          ✅ Review complete! {reviews.length} file{reviews.length !== 1 ? "s" : ""} reviewed.
        </div>
      )}
      <ReviewFeed reviews={reviews} />
    </div>
  );
}

export default App;