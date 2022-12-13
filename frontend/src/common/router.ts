import { createRouter, createWebHistory } from "vue-router";
import ExamplePage from "../pages/ExamplePage.vue";
import EventPage from "../pages/EventPage.vue";
import EventCreatePage from "../pages/EventCreatePage.vue";

// Register all appliaction paths here

export default createRouter({
    history: createWebHistory(),
    routes: [
        { path: "/", component: ExamplePage },
        { path: "/event", component: EventPage },
        { path: "/event/new", component: EventCreatePage },
    ]
});
