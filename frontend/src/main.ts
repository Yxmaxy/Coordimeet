import { createPinia } from 'pinia';
import { createApp } from 'vue'

import router from '@/utils/router';
import App from '@/pages/App.vue'

import '@/styles/global.scss'
import '@/styles/index.css'

const pinia = createPinia();

createApp(App).use(pinia).use(router).mount('#app');
