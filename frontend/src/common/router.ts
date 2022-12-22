import { createRouter, createWebHashHistory } from "vue-router";
import HomePage from "../pages/HomePage.vue";
import EventPage from "../pages/EventPage.vue";
import EventCreatePage from "../pages/EventCreatePage.vue";
import EventListPage from "../pages/EventListPage.vue";

// Register all appliaction paths here

export default createRouter({
    history: createWebHashHistory(),
    routes: [
        { path: "/", component: HomePage },
        { path: "/event/:id", component: EventPage },
        { path: "/event/new", component: EventCreatePage },
        { path: "/event/list", component: EventListPage },
        { path: "/:catchAll(.*)", redirect: () => "" },
    ]
});
