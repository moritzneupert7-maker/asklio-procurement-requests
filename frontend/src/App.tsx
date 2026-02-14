import { useEffect, useState } from "react";
import "./App.css";
import { createFromOffer, listRequests } from "./api";

export default function App() {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const [requests, setRequests] = useState<any[]>([]);
  const [offerFile, setOfferFile] = useState<File | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);
  const [showHistory, setShowHistory] = useState(false);
  const [loading, setLoading] = useState(false);

  async function refresh() {
    const data = await listRequests();
    setRequests(data);
  }

  useEffect(() => {
    refresh().catch((e) => setError(String(e)));
  }, []);

  async function onCreateFromOffer() {
    if (!offerFile) return;
    setError(null);
    setMessage(null);
    setLoading(true);
    try {
      await createFromOffer(offerFile);
      setMessage("Request created from offer successfully.");
      setOfferFile(null);
      await refresh();
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setLoading(false);
    }
  }

  const latestRequest = requests.length ? requests[0] : null;
  const olderRequests = requests.length > 1 ? requests.slice(1) : [];

  return (
    <div style={{ maxWidth: 900, margin: "0 auto", padding: 16 }}>
      <h2>Procurement Requests</h2>

      {error && <pre style={{ background: "#fee", padding: 12 }}>{error}</pre>}
      {message && (
          <div style={{ background: "#e5ffe5", padding: 12, borderRadius: 6, marginBottom: 12 }}>
          {message}
          </div>
       )}

      <div style={{ marginTop: 12 }}>
        <h4>Upload offer to create a request</h4>
        <input
          style={{ marginTop: 8 }}
          type="file"
          accept=".txt,.pdf"
          onChange={(e) => setOfferFile(e.target.files?.[0] ?? null)}
        />
        <div style={{ marginTop: 8 }}>
          <button disabled={!offerFile || loading} onClick={onCreateFromOffer}>
            {loading ? "Creating..." : "Create request from offer"}
          </button>
        </div>
      </div>

      <hr style={{ margin: "16px 0" }} />

      <button onClick={() => refresh().catch((e) => setError(String(e)))}>Refresh overview</button>

      {latestRequest && (
    <>
      <h4 style={{ marginTop: 12 }}>Latest request</h4>
      <table style={{ width: "100%", marginTop: 8, borderCollapse: "collapse" }}>
        <thead>
          <tr>
            <th align="left">ID</th>
            <th align="left">Title</th>
            <th align="left">Vendor</th>
            <th align="left">Total</th>
            <th align="left">Status</th>
            <th align="left">Commodity</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td>{latestRequest.id}</td>
            <td>{latestRequest.title}</td>
            <td>{latestRequest.vendor_name}</td>
            <td>{latestRequest.total_cost}</td>
            <td>{latestRequest.current_status}</td>
            <td>
              {latestRequest.commodity_group_id ?? "-"}
              {latestRequest.commodity_group?.name
                ? ` – ${latestRequest.commodity_group.name}`
                : ""}
            </td>
          </tr>
        </tbody>
      </table>
    </>
  )}

  {olderRequests.length > 0 && (
  <div style={{ marginTop: 16 }}>
    <button type="button" onClick={() => setShowHistory((v) => !v)}>
      {showHistory ? "Hide history" : `Show history (${olderRequests.length})`}
    </button>
    {showHistory && (
        <table style={{ width: "100%", marginTop: 8, borderCollapse: "collapse" }}>
          <thead>
            <tr>
              <th align="left">ID</th>
              <th align="left">Title</th>
              <th align="left">Vendor</th>
              <th align="left">Total</th>
              <th align="left">Status</th>
              <th align="left">Commodity</th>
            </tr>
          </thead>
          <tbody>
           {olderRequests.map((r) => (
              <tr key={r.id}>
                <td>{r.id}</td>
                <td>{r.title}</td>
                <td>{r.vendor_name}</td>
                <td>{r.total_cost}</td>
                <td>{r.current_status}</td>
                <td>
                  {r.commodity_group_id ?? "-"}
                  {r.commodity_group?.name ? ` – ${r.commodity_group.name}` : ""}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
    )}
      </div>
    );
  }
