const API_BASE = "http://127.0.0.1:8000";

export type ProcurementRequestCreate = {
  requestor_name: string;
  title: string;
  department: string;
  vendor_name: string;
  vendor_vat_id?: string;
  order_lines: { description: string; unit_price: number; amount: number; unit?: string }[];
};

export async function createRequest(payload: ProcurementRequestCreate) {
  const res = await fetch(`${API_BASE}/requests`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function listRequests() {
  const res = await fetch(`${API_BASE}/requests`);
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function uploadOffer(requestId: number, file: File) {
  const formData = new FormData();
  formData.append("file", file); // common fetch+FormData upload pattern [web:428]

  const res = await fetch(`${API_BASE}/requests/${requestId}/upload-offer`, {
    method: "POST",
    body: formData,
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function extractOffer(requestId: number) {
  const res = await fetch(`${API_BASE}/requests/${requestId}/extract-offer`, { method: "POST" });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function createFromOffer(file: File) {
  const formData = new FormData();
  formData.append("file", file);

  const res = await fetch(`${API_BASE}/requests/create-from-offer`, {
    method: "POST",
    body: formData,
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}
