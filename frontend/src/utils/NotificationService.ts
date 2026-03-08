import { PushSubscriptionHelper } from "django-simple-notifications";
import { getCookie } from "django-session-api";


export default new PushSubscriptionHelper({
    baseUrl: import.meta.env.VITE_NOTIFICATIONS_URL,
    vapidPublicKey: import.meta.env.VITE_NOTIFICATIONS_VAPID_PUBLIC_KEY,
    appName: "coordimeet",
    serverRequestParameters: {
        credentials: "include",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCookie("csrftoken") ?? "",
        },
    },
});
