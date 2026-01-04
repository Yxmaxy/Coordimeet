import { clientsClaim } from "workbox-core"
import { precacheAndRoute, cleanupOutdatedCaches } from "workbox-precaching"
import { serviceWorkerPushHandler } from "django-simple-notifications";

declare let self: ServiceWorkerGlobalScope;
declare const __APP_VERSION__: string | undefined;
let APP_VERSION = "0.0.0";
if (typeof __APP_VERSION__ !== "undefined") {
    APP_VERSION = __APP_VERSION__ as string;
}

const DEBUG = import.meta.env.MODE === "development";
const CACHE_NAME = `coordimeet-cache-v${APP_VERSION}`;

clientsClaim();

cleanupOutdatedCaches();
precacheAndRoute(self.__WB_MANIFEST);

self.addEventListener("install", () => self.skipWaiting());
self.addEventListener("activate", () => self.clients.claim());

if (DEBUG) console.log("Service worker is running");

// Handle fetch events
async function handleNetworkFirstRequest(request: Request) {
    const cache = await caches.open(CACHE_NAME);
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

self.addEventListener("push", (event) => {
    serviceWorkerPushHandler(self.registration, event);
});

self.addEventListener("notificationclick", (event: NotificationEvent) => {
    const notification = event.notification;
    const url = notification.data.url;
    if (url) {
        event.waitUntil(self.clients.openWindow(url));
        notification.close();
    }
});
