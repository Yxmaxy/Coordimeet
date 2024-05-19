import axios from "axios";
import { getCookie } from "@/utils/cookies";
import { retrieveAccessToken, removeTokens } from "@/utils/tokens";

axios.defaults.baseURL = import.meta.env.VITE_BACKEND_URL;
axios.defaults.withCredentials = true;
axios.defaults.headers.post["X-CSRFToken"] = getCookie("csrftoken");

// append token to request header
axios.interceptors.request.use(async config => {
    const token = await retrieveAccessToken();
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

// sliding access token expired, redirect to login
axios.interceptors.response.use(undefined, async error => {
    if (error.config && error.response?.status === 401) {  // TODO: extend with detail ?
        await removeTokens();
        window.location.href = "/";
    }
    return Promise.reject(error);
});

export default axios;
