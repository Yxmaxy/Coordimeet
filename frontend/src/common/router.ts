import { createRouter, createWebHashHistory } from "vue-router";
import { developmentMode } from "./globals";
import { useUserStore } from "./stores/UserStore";
import HomePage from "../pages/HomePage.vue";
import EventPage from "../pages/EventPage.vue";
import EventCreatePage from "../pages/EventCreatePage.vue";
import EventListPage from "../pages/EventListPage.vue";

// Register all appliaction paths here

const router = createRouter({
    history: createWebHashHistory(),
    routes: [
        { path: "/", component: HomePage, name: "home" },
        { path: "/event/:id", component: EventPage },
        { path: "/event/new", component: EventCreatePage },
        { path: "/event/list", component: EventListPage },
        { path: "/:catchAll(.*)", redirect: () => "/" },
    ]
});

if (!developmentMode)
    router.beforeEach((to, from, next) => {
        const userStore = useUserStore();
        if (to.name === "home" && userStore.isLoggedIn)
            return next("/event/list");
        if (to.name !== "home" && !userStore.isLoggedIn)
            return next("/");
        next();
    });

export default router;