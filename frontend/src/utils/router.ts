import { createRouter, createWebHistory } from "vue-router";

import Event from "@/pages/Event.vue";
import EventCreate from "@/pages/EventCreate.vue";
import EventList from "@/pages/EventList.vue";

import GroupCreate from "@/pages/GroupCreate.vue";
import GroupList from "@/pages/GroupList.vue";

const router = createRouter({
    history: createWebHistory(),
    routes: [
        { path: "/", redirect: { name: "event_list" } },
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
});

export default router;