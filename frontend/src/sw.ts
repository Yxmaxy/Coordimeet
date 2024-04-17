import { cleanupOutdatedCaches, precacheAndRoute } from "workbox-precaching"
import { clientsClaim } from "workbox-core"

declare let self: ServiceWorkerGlobalScope;

clientsClaim();

// precacheAndRoute(self.__WB_MANIFEST);

cleanupOutdatedCaches();

self.addEventListener("install", () => self.skipWaiting());
self.addEventListener("activate", () => self.clients.claim());

console.log("hello 2!")

// Notifications
let notificationsEnabled = true;
if (!self.registration.showNotification) {
    console.log("Notifications are not supported");
    notificationsEnabled = false;
}
if (Notification.permission === "denied") {
    console.log("Notifications are blocked");
    notificationsEnabled = false;
}
if (!self.registration.pushManager) {
    console.log("Push notifications are not supported");
    notificationsEnabled = false;
}

if (notificationsEnabled) {
    subscribeToNotifications();
}

function urlB64ToUint8Array(base64String: any) {
    const padding = '='.repeat((4 - base64String.length % 4) % 4);
    const base64 = (base64String + padding)
        .replace(/\-/g, '+')
        .replace(/_/g, '/');

    const rawData = atob(base64);
    const outputArray = new Uint8Array(rawData.length);
    for (let i = 0; i < rawData.length; i++) {
        outputArray[i] = rawData.charCodeAt(i);
    }

    return outputArray;

}

async function subscribeToNotifications() {
    let subscription = await self.registration.pushManager.getSubscription();
    if (subscription) {
        console.log("I am already subscribed");
        sendSubscriptionData(subscription);
        return;
    }
    const convertedVapidKey = urlB64ToUint8Array(import.meta.env.VITE_VAPID_PUBLIC_KEY);
    const options = {
        userVisibleOnly: true,
        applicationServerKey: convertedVapidKey,
    }
    
    subscription = await self.registration.pushManager.subscribe(options);
    sendSubscriptionData(subscription);
    console.log("Just subscribed!")
}

async function sendSubscriptionData(subscription: PushSubscription) {
    const browser = navigator.userAgent.match(/(firefox|msie|chrome|safari|trident)/ig)![0].toLowerCase();
    const data = {
        group: "Some other group",
        status_type: "subscribe",
        subscription: subscription.toJSON(),
        browser: browser,
        user_agent: navigator.userAgent,
    };

    const res = await fetch(`${import.meta.env.VITE_BACKEND_URL}/notifications/save_information`, {
        method: "POST",
        body: JSON.stringify(data),
        headers: {
            "content-type": "application/json"
        },
        credentials: "include"
    });

    console.log(res);
}

self.addEventListener("push", async (event: PushEvent) => {
    console.log("push called")
    console.log(event.data?.json().data.message);

    event.waitUntil(self.registration.showNotification("Testing", {
        body: "Welcome",
    }));
});
