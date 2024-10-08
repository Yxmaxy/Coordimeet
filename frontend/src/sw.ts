import { clientsClaim } from "workbox-core"
import { precacheAndRoute, cleanupOutdatedCaches } from "workbox-precaching"

import { retrieveTokens } from "@/utils/tokens";

declare let self: ServiceWorkerGlobalScope;

const DEBUG = import.meta.env.MODE === "development";

clientsClaim();

// cache assets defined in globPatterns
precacheAndRoute(self.__WB_MANIFEST);
cleanupOutdatedCaches();

self.addEventListener("install", () => self.skipWaiting());
self.addEventListener("activate", () => self.clients.claim());

if (DEBUG) console.log("Service worker is running");

// Helpers
function __urlB64ToUint8Array(base64String: any) {
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

// Register user to notifications
function registerNotifications(userID: Number) {
    // checks that the notifications are supported.

    if (!self.registration.showNotification) {
        console.warn("Notifications are not supported");
        return;
    }
    if (!self.registration.pushManager) {
        console.warn("Push notifications are not supported");
        return;
    }
    if (Notification.permission === "denied") {
        console.warn("Notifications are blocked");
        return;
    }
    if (Notification.permission === "granted") {
        subscribeUserToNotifications(userID);
        return;
    }
}

async function subscribeUserToNotifications(userID: Number) {
    // tries to subscribe user to notifications if they are not already subscribed
    const oldSubscription = await self.registration.pushManager.getSubscription();
    if (oldSubscription) {
        sendSubscriptionData(oldSubscription, userID);
        return;
    }

    // register user to notifications
    const convertedVapidKey = __urlB64ToUint8Array(import.meta.env.VITE_VAPID_PUBLIC_KEY);
    const options = {
        userVisibleOnly: true,
        applicationServerKey: convertedVapidKey,
    }
    const newSubscription = await self.registration.pushManager.subscribe(options);
    sendSubscriptionData(newSubscription, userID);
}

async function sendSubscriptionData(subscription: PushSubscription, userID: Number) {
    const browser = navigator.userAgent.match(/(firefox|msie|chrome|safari|trident)/ig)![0].toLowerCase();
    const data = {
        user: userID,
        status_type: "subscribe",
        subscription: subscription.toJSON(),
        browser: browser,
        user_agent: navigator.userAgent,
    };

    try {
        const { accessToken } = await retrieveTokens();
        const response = await fetch(`${import.meta.env.VITE_BACKEND_URL}/notifications/save_information/`, {
            method: "POST",
            body: JSON.stringify(data),
            headers: {
                "content-type": "application/json",
                "Authorization": `Bearer ${accessToken}`,
            },
            credentials: "include"
        });
        if (!response.ok) {
            console.error("Failed to subscribe user to notifications", response.statusText);
            return;
        } else {
            if (DEBUG) console.log("Subscribed successfully!");
        }
    } catch (error) {
        console.error(error);
    }
}

function unsubscribeUserFromNotifications() {
    self.registration.pushManager.getSubscription().then((subscription) => {
        if (subscription) {
            subscription.unsubscribe();
        }
    });
}

async function resubscribeUserToNotifications(userID: Number) {
    const previousSubscription = await self.registration.pushManager.getSubscription()
    if (previousSubscription) {
        previousSubscription.unsubscribe();
    }   
    registerNotifications(userID);
}

// Handle push notifications
self.addEventListener("push", async (event: PushEvent) => {
    const notificationData = event.data?.json();

    if (!notificationData) {
        console.error("No notification data");
        return;
    }
    event.waitUntil(self.registration.showNotification(notificationData.head, {
        body: notificationData.body,
        icon: notificationData.icon,
        badge: notificationData.badge,
        data: {
            url: notificationData.url,
        },
    }));

    // try resubscribing
    const { userID } = notificationData;
    if (userID) {
        resubscribeUserToNotifications(userID);
    }
});

self.addEventListener("notificationclick", (event: NotificationEvent) => {
    const notification = event.notification;
    const url = notification.data.url;
    if (url) {
        event.waitUntil(self.clients.openWindow(url));
        notification.close();
    }
});

// Handle messages from main thread
self.addEventListener("message", (event: any) => {
    if (DEBUG) console.log("Received message!")
    if (event.data?.type === "REGISTER_NOTIFICATIONS") {
        const userID = event.data.user_id;
        if (!userID) {
            console.error("No user ID provided");
            return;
        }
        registerNotifications(userID);
    }
    if (event.data?.type === "UNSUBSCRIBE_NOTIFICATIONS") {
        unsubscribeUserFromNotifications();
    }
});

// Handle fetch events
async function handleNetworkFirstRequest(request: Request) {
    const cache = await caches.open("coordimeet-cache");
    try {
        const response = await fetch(request);
        cache.put(request, response.clone());
        if (DEBUG) console.log("Normal response");
        return response;
    } catch (error) {
        const cachedResponse = await cache.match(request);
        if (cachedResponse) {
            if (DEBUG) console.log("Serving cached response");
            return cachedResponse;
        }
        throw error;
    }
}

self.addEventListener("fetch", (event: FetchEvent) => {
    if (event.request.method !== "GET")
        return;
    event.respondWith(handleNetworkFirstRequest(event.request));
});
