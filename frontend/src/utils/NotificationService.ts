import { PushSubscriptionHelper } from "django-simple-notifications";
import { getCookie } from "django-session-api";


export default new PushSubscriptionHelper({
    baseUrl: import.meta.env.VITE_NOTIFICATIONS_URL,
    appName: import.meta.env.VITE_NOTIFICATIONS_APP_NAME,
    vapidPublicKey: import.meta.env.VITE_NOTIFICATIONS_VAPID_PUBLIC_KEY,
    serverRequestParameters: {
        credentials: "include",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCookie("csrftoken") ?? "",
        },

    },
});
