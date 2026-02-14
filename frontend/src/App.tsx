import { useEffect, useState } from "react";
import "./App.css";
import { createRequest, extractOffer, listRequests, uploadOffer, type ProcurementRequestCreate } from "./api";

export default function App() {
  const [requests, setRequests] = useState<any[]>([]);
  const [createdId, setCreatedId] = useState<number | null>(null);
  const [offerFile, setOfferFile] = useState<File | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);
  const [showHistory, setShowHistory] = useState(false);

  const [form] = useState<ProcurementRequestCreate>({
    requestor_name: "Moritz Neupert",
    title: "New Procurement Request",
    department: "Marketing",
    vendor_name: "Pending – upload offer",
    vendor_vat_id: "",
    order_lines: [{ description: "Pending – upload offer", unit_price: 1, amount: 1, unit: "pcs" }],
  });

  async function refresh() {
    const data = await listRequests();
    setRequests(data);
  }

  useEffect(() => {
    refresh().catch((e) => setError(String(e)));
  }, []);

  async function onCreate() {
    setError(null);
    try {
      const created = await createRequest(form);
      setCreatedId(created.id);
      await refresh();
    } catch (e: any) {
      setError(e?.message ?? String(e));
    }
  }

  async function onUpload() {
    if (!createdId || !offerFile) return;
    setError(null);
    setMessage(null);
    try {
      await uploadOffer(createdId, offerFile);
      setMessage("Offer uploaded successfully.");
      await refresh();
    } catch (e: any) {
      setError(e?.message ?? String(e));
    }
  }

  async function onExtract() {
    if (!createdId) return;
    setError(null);
    setMessage(null);
    try {
      await extractOffer(createdId);
      setMessage("Offer extracted and request updated.");
      await refresh();
    } catch (e: any) {
      setError(e?.message ?? String(e));
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

      <button onClick={onCreate}>Create request</button>

      {createdId && (
        <div style={{ marginTop: 12, padding: 16, background: "#f0f4ff", borderRadius: 8, border: "1px solid #b3c6ff" }}>
          <div>Created request id: {createdId}</div>
          <p style={{ marginTop: 8, fontWeight: 500 }}>
            Please upload an offer document to automatically fill in vendor details, order lines, and pricing.
          </p>

          <input
            style={{ marginTop: 8 }}
            type="file"
            accept=".txt"
            onChange={(e) => setOfferFile(e.target.files?.[0] ?? null)}
          />

          <div style={{ marginTop: 8, display: "flex", gap: 8 }}>
            <button disabled={!offerFile} onClick={onUpload}>Upload offer</button>
            <button onClick={onExtract}>Extract & autofill</button>
          </div>
        </div>
      )}

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
