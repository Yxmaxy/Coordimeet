import { createRouter, createWebHistory } from "vue-router";
import HomePage from "../pages/HomePage.vue";
import EventPage from "../pages/EventPage.vue";
import EventCreatePage from "../pages/EventCreatePage.vue";
import EventListPage from "../pages/EventListPage.vue";
import EventAttendPage from "../pages/EventAttendPage.vue";

// Register all appliaction paths here

export default createRouter({
    history: createWebHistory(),
    routes: [
        { path: "/", component: HomePage },
        { path: "/event", component: EventPage },
        { path: "/event/new", component: EventCreatePage },
        { path: "/event/list", component: EventListPage },
        { path: "/event/attend", component: EventAttendPage },
        { path: "/:catchAll(.*)", redirect: () => "" },
    ]
});
