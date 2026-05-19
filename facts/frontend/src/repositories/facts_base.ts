import axios from "axios";

const FACTS_URL = import.meta.env.VITE_FACTS_URL ?? "http://localhost:8001"

export default axios.create({
  baseURL: FACTS_URL,
  headers: {
    "Content-type": "application/json"
  }
});