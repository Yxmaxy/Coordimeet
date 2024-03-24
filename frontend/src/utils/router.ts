import { createRouter, createWebHistory } from "vue-router";

import { useStoreUser } from "@/stores/storeUser";

import Home from "@/pages/Home.vue";
import Event from "@/pages/Event.vue";
import EventCreate from "@/pages/EventCreate.vue";
import EventList from "@/pages/EventList.vue";

const router = createRouter({
    history: createWebHistory(),
    routes: [
        { path: "/", component: Home, name: "home" },
        { path: "/event/:uuid", component: Event, name: "event"},
        { path: "/event/new", component: EventCreate, name: "new" },
        { path: "/event/list", component: EventList, name: "list" },
        { path: "/:catchAll(.*)", redirect: () => "/" },
    ]
});

router.beforeEach(async (to, from) => {
    // scroll to top on route change
    window.scrollTo(0, 0);

    // retrieve the user
    const userStore = useStoreUser();
    await userStore.retrieveUser();
    if (from.name === to.name)
        return false;
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