import axios from "axios";

const EBSI_URL = import.meta.env.VITE_EBSI_URL ?? "http://localhost:8000"

export default axios.create({
  baseURL: EBSI_URL,
  headers: {
    "Content-type": "application/json"
  }
});