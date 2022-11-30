import { createRouter, createWebHistory } from "vue-router";
import ExamplePage from "../pages/ExamplePage.vue";

// Register all appliaction paths here

export default createRouter({
    history: createWebHistory(),
    routes: [
        { path: "/", component: ExamplePage },
    ]
});
