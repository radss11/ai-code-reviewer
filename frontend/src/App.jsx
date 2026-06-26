import { useState } from "react";
import PRInput from "./components/PRInput";
import ReviewFeed from "./components/ReviewFeed";
import useWebSocket from "./hooks/useWebSocket";

function App() {
  const [prId, setPrId] = useState(null);
  const [reviews, setReviews] = useState([]);
  const [done, setDone] = useState(false);
  const [loading, setLoading] = useState(false);

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
    setLoading(true);

    const res = await fetch("http://localhost:8000/review", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ pr_url: url }),
    });
    const data = await res.json();
    setPrId(data.pr_id);
  };

  return (
    <div style={{ maxWidth: 800, margin: "40px auto", fontFamily: "sans-serif", padding: "0 20px" }}>
      <h1>🔍 AI Code Review</h1>
      <PRInput onSubmit={handleSubmit} loading={loading} />
      {loading && <p>⏳ Reviewing files...</p>}
      {done && <p>✅ Review complete!</p>}
      <ReviewFeed reviews={reviews} />
    </div>
  );
}

export default App;