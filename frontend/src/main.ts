import { createPinia } from "pinia";
import { createApp } from "vue"
import { registerSW } from "virtual:pwa-register";

import router from "@/utils/router";
import { updateAppTheme } from "@/utils/theme";

import App from "@/pages/App.vue"

import "@/styles/index.css"

const pinia = createPinia();

createApp(App).use(pinia).use(router).mount("#app");
updateAppTheme();

registerSW();
