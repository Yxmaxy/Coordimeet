import { createDjangoApi } from "django-session-api";
import router from "./router";

const api = createDjangoApi({
    baseUrl: import.meta.env.VITE_BASE_BACKEND_API_URL,
    onAuthError: () => {
        router.push({ name: "home" });
    },
});

export default api;
