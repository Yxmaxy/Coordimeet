import { createRouter, createWebHashHistory } from "vue-router";

import { useUserStore } from "@/stores/UserStore";

import Home from "@/pages/Home.vue";
import Event from "@/pages/Event.vue";
import EventCreate from "@/pages/EventCreate.vue";
import EventList from "@/pages/EventList.vue";

const router = createRouter({
    history: createWebHashHistory(),
    routes: [
        { path: "/", component: Home, name: "home" },
        { path: "/event/:id", component: Event, name: "event"},
        { path: "/event/new", component: EventCreate, name: "new" },
        { path: "/event/list", component: EventList, name: "list" },
        { path: "/:catchAll(.*)", redirect: () => "/" },
    ]
});

router.beforeEach(async (to, from) => {
    const userStore = useUserStore();
    const isLoggedIn = await userStore.loginUser();
    if (from.name === to.name)
        return false;
    if (to.name === "event") {
        if (!isLoggedIn) {
            alert("Please log in and re-visit this link");
            return "/";
        }
        return true;
    }
    if (to.name === "home" && isLoggedIn)
        return "/event/list";
    if (to.name !== "home" && !isLoggedIn)
        return "/";
    return true;
});

export default router;