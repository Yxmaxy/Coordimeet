import axios from "axios";
import { getCookie } from "@/utils/cookies";
import { saveAccessToken, retrieveTokens, removeTokens } from "@/utils/tokens";

axios.defaults.baseURL = import.meta.env.VITE_BACKEND_URL;
axios.defaults.withCredentials = true;
axios.defaults.headers.post["X-CSRFToken"] = getCookie("csrftoken");

// append token to request header
axios.interceptors.request.use(async config => {
    const { accessToken } = await retrieveTokens();
    if (accessToken) {
        config.headers.Authorization = `Bearer ${accessToken}`;
    }
    return config;
});

// token expired, request new token if possible
axios.interceptors.response.use(undefined, async error => {
    if (error.config && error.response?.status === 401) {
        if (error.config.url === "/users/token/refresh/") {
            // If it is, reject the promise
            return Promise.resolve(error);
        }
        try {
            const { refreshToken } = await retrieveTokens();
            const response = await axios.post("/users/token/refresh/", {
                refresh: refreshToken,
            });
            // set new access token
            const newAccessToken = response.data.access
            saveAccessToken(newAccessToken);
            error.config.headers.Authorization = `Bearer ${newAccessToken}`;
            return axios(error.config);
        } catch (error) {
            await removeTokens();  // TODO: make request to backend
            window.location.href = "/login";
        }
    }
    return Promise.reject(error);
});

export default axios;
