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
        // { path: "/:catchAll(.*)", redirect: () => "/" },
    ]
});

router.beforeEach(async (to, from) => {
    const userStore = useUserStore();
    console.log("started login check")
    const isLoggedIn = await userStore.loginUser();
    console.log(isLoggedIn);
    console.log(from, to);
    if (from.name === to.name)
        return false;
    if (to.name === "event") {
        console.log("event redirect");
        if (!isLoggedIn) {
            alert("Please log in and re-visit this link");
            return "/";
        }
        return true;
    }
    if (to.name === "home" && isLoggedIn) {
        console.log("home -> list");
        return "/event/list";
    }
    if (to.name !== "home" && !isLoggedIn) {
        console.log("* -> home");
        return "/";
    }
    return true;
});

export default router;