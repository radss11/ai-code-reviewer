import { useState } from "react";

function PRInput({ onSubmit, loading }) {
  const [error, setError] = useState("");

  const handleSubmit = (e) => {
    e.preventDefault();
    const url = e.target.url.value.trim();

    if (!url) {
      setError("Please enter a GitHub PR URL");
      return;
    }

    if (!url.includes("github.com") || !url.includes("/pull/")) {
      setError("Invalid URL. Format: https://github.com/owner/repo/pull/123");
      return;
    }

    setError("");
    onSubmit(url);
  };

  return (
    <div style={{ marginBottom: 20 }}>
      <form onSubmit={handleSubmit} style={{ display: "flex", gap: 10 }}>
        <input
          name="url"
          placeholder="https://github.com/owner/repo/pull/123"
          style={{
            flex: 1, padding: "8px 12px", fontSize: 14,
            borderRadius: 6, border: error ? "1px solid #dc2626" : "1px solid #ccc",
            background: "#1f2937", color: "white"
          }}
          disabled={loading}
        />
        <button
          type="submit"
          disabled={loading}
          style={{
            padding: "8px 16px", background: loading ? "#6b7280" : "#2563eb",
            color: "white", border: "none", borderRadius: 6,
            cursor: loading ? "not-allowed" : "pointer", fontWeight: "bold"
          }}
        >
          {loading ? "Reviewing..." : "Review"}
        </button>
      </form>
      {error && <p style={{ color: "#dc2626", fontSize: 13, margin: "6px 0 0" }}>{error}</p>}
    </div>
  );
}

export default PRInput;