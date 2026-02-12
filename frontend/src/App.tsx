import { useEffect, useState } from "react";
import "./App.css";
import { createRequest, extractOffer, listRequests, uploadOffer, type ProcurementRequestCreate } from "./api";

export default function App() {
  const [requests, setRequests] = useState<any[]>([]);
  const [createdId, setCreatedId] = useState<number | null>(null);
  const [offerFile, setOfferFile] = useState<File | null>(null);
  const [error, setError] = useState<string | null>(null);

  const [form, setForm] = useState<ProcurementRequestCreate>({
    requestor_name: "John Doe",
    title: "Adobe Creative Cloud Subscription",
    department: "Creative Marketing Department",
    vendor_name: "Global Tech Solutions",
    vendor_vat_id: "DE987654321",
    order_lines: [{ description: "Adobe Photoshop License", unit_price: 150, amount: 10, unit: "licenses" }],
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
    try {
      await uploadOffer(createdId, offerFile);
      await refresh();
    } catch (e: any) {
      setError(e?.message ?? String(e));
    }
  }

  async function onExtract() {
    if (!createdId) return;
    setError(null);
    try {
      await extractOffer(createdId);
      await refresh();
    } catch (e: any) {
      setError(e?.message ?? String(e));
    }
  }

  return (
    <div style={{ maxWidth: 900, margin: "0 auto", padding: 16 }}>
      <h2>Procurement Requests</h2>

      {error && <pre style={{ background: "#fee", padding: 12 }}>{error}</pre>}

      <button onClick={onCreate}>Create request</button>

      {createdId && (
        <div style={{ marginTop: 12 }}>
          <div>Created request id: {createdId}</div>

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

      <table style={{ width: "100%", marginTop: 12 }}>
        <thead>
          <tr>
            <th align="left">ID</th>
            <th align="left">Title</th>
            <th align="left">Vendor</th>
            <th align="left">Total</th>
            <th align="left">Status</th>
          </tr>
        </thead>
        <tbody>
          {requests.map((r) => (
            <tr key={r.id}>
              <td>{r.id}</td>
              <td>{r.title}</td>
              <td>{r.vendor_name}</td>
              <td>{r.total_cost}</td>
              <td>{r.current_status}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
