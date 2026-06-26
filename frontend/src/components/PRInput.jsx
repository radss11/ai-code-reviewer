function PRInput({ onSubmit, loading }) {
  const handleSubmit = (e) => {
    e.preventDefault();
    const url = e.target.url.value.trim();
    if (url) onSubmit(url);
  };

  return (
    <form onSubmit={handleSubmit} style={{ display: "flex", gap: 10, marginBottom: 20 }}>
      <input
        name="url"
        placeholder="https://github.com/owner/repo/pull/123"
        style={{ flex: 1, padding: "8px 12px", fontSize: 14, borderRadius: 6, border: "1px solid #ccc" }}
        disabled={loading}
      />
      <button
        type="submit"
        disabled={loading}
        style={{ padding: "8px 16px", background: "#2563eb", color: "white", border: "none", borderRadius: 6, cursor: "pointer" }}
      >
        {loading ? "Reviewing..." : "Review"}
      </button>
    </form>
  );
}

export default PRInput;