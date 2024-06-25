import { createRouter, createWebHistory } from "vue-router";

import { useStoreUser } from "@/stores/storeUser";

// import Home from "@/pages/Home.vue";  NOTE: Currently not used
import Login from "@/pages/Login.vue";

import Event from "@/pages/Event.vue";
import EventCreate from "@/pages/EventCreate.vue";
import EventList from "@/pages/EventList.vue";

import GroupCreate from "@/pages/GroupCreate.vue";
import GroupList from "@/pages/GroupList.vue";

const router = createRouter({
    history: createWebHistory(),
    routes: [
        { path: "/", component: Login, name: "login" },
        { path: "/event/:uuid", component: Event, name: "event"},
        { path: "/event/new/:uuid?", component: EventCreate, name: "event_new" },
        { path: "/event/edit/:uuid", component: EventCreate, name: "event_edit" },
        { path: "/event/list", component: EventList, name: "event_list" },
        { path: "/group/new", component: GroupCreate, name: "group_new" },
        { path: "/group/edit/:id", component: GroupCreate, name: "group_edit" },
        { path: "/group/list", component: GroupList, name: "group_list" },
        { path: "/:catchAll(.*)", redirect: () => "/" },
    ]
});

router.beforeEach(async (to, from) => {
    // scroll to top on route change
    window.scrollTo(0, 0);

    if (from.name === to.name)
        return false;

    // retrieve is logged in
    const userStore = useStoreUser();
    const isLoggedIn = await userStore.isLoggedIn();

    // redirect to login if not logged in
    if (isLoggedIn && ["login"].includes(to.name as string))
        return "/event/list";
    if (!isLoggedIn && !["login", "event"].includes(to.name as string))
        return "/";
    return true;
});

export default router;