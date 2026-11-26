import axios from "axios";

const api = axios.create({
  baseURL: "/api",
  timeout: 15000,
});

export async function getHealth() {
  const { data } = await api.get("/health");
  return data;
}

export async function getStats() {
  const { data } = await api.get("/stats");
  return data;
}

export async function getCompanies() {
  const { data } = await api.get("/companies");
  return data;
}

export async function getTranscripts(company = null, limit = 100) {
  const params = { limit };
  if (company) params.company = company;
  const { data } = await api.get("/transcripts", { params });
  return data;
}

export async function getTranscript(id) {
  const { data } = await api.get(`/transcripts/${id}`);
  return data;
}

export function getTranscriptPdfUrl(id) {
  return `/api/transcripts/${id}/pdf`;
}

export default api;

