import axios from "axios";
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
        { path: "/event/:id", component: EventPage, name: "event"},
        { path: "/event/new", component: EventCreatePage, name: "new" },
        { path: "/event/list", component: EventListPage, name: "list" },
        { path: "/:catchAll(.*)", redirect: () => "/" },
    ]
});

if (developmentMode)
    router.beforeEach(async (to, from) => {
        const userStore = useUserStore();
        await userStore.loginUser();
        if (to.name === "event") {
            if (!userStore.isLoggedIn) {
                alert("Please log in and re-visit this link");
                return "/";
            }
            return true;
        }
        if (to.name === "home" && userStore.isLoggedIn)
            return "/event/list";
        if (to.name !== "home" && !userStore.isLoggedIn)
            return "/";
        return true;
    });

export default router;