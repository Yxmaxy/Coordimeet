import axios from "axios";
import { getCookie } from "@/utils/cookies";
import { retrieveAccessToken, removeTokens } from "@/utils/tokens";

// axios.defaults.baseURL = "http://127.0.0.1:8000"//;
axios.defaults.baseURL = import.meta.env.VITE_BACKEND_URL;
axios.defaults.withCredentials = true;
axios.defaults.headers.post["X-CSRFToken"] = getCookie("csrftoken");

// append token to request header
axios.interceptors.request.use(config => {
    const token = retrieveAccessToken();
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

// sliding access token expired, redirect to login
axios.interceptors.response.use(undefined, async error => {
    if (error.config && error.response && error.response.status === 401) {
        removeTokens();
        window.location.href = "/";
    }
});

export default axios;
