function FileCard({ review }) {
  const verdictColor = {
    approved: "#16a34a",
    needs_changes: "#d97706",
    critical: "#dc2626",
  };

  return (
    <div style={{ border: "1px solid #e5e7eb", borderRadius: 8, padding: 16, marginBottom: 16 }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <h3 style={{ margin: 0, fontSize: 14, fontFamily: "monospace" }}>{review.filename}</h3>
        <span style={{ color: verdictColor[review.verdict], fontWeight: "bold", fontSize: 13 }}>
          {review.verdict}
        </span>
      </div>
      <p style={{ color: "#6b7280", fontSize: 13, margin: "8px 0" }}>{review.summary}</p>
      {review.issues?.length > 0 && (
        <div>
          {review.issues.map((issue, i) => (
            <div key={i} style={{ background: "#fef9c3", borderRadius: 6, padding: 10, marginTop: 8 }}>
              <span style={{ fontSize: 12, fontWeight: "bold", color: "#92400e" }}>
                [{issue.severity}]
              </span>
              <code style={{ display: "block", fontSize: 12, margin: "4px 0", color: "#374151" }}>
                {issue.line}
              </code>
              <p style={{ fontSize: 13, margin: 0, color: "#374151" }}>{issue.comment}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function ReviewFeed({ reviews }) {
  if (reviews.length === 0) return null;
  return (
    <div>
      <h2>Review Results</h2>
      {reviews.map((r, i) => (
        <FileCard key={i} review={r} />
      ))}
    </div>
  );
}

export default ReviewFeed;