import { createDjangoApi } from "django-session-api";

const api = createDjangoApi({
    baseUrl: import.meta.env.VITE_BASE_BACKEND_API_URL,
    loginUrl: import.meta.env.VITE_LOGIN_URL,
});

export default api;
