import { createPinia } from 'pinia';
import { createApp } from 'vue'

import router from '@/utils/router';
import { updateAppTheme } from '@/utils/theme';
import App from '@/pages/App.vue'

import '@/styles/global.scss'
import '@/styles/index.css'
import '@/styles/ui.css'

const pinia = createPinia();

createApp(App).use(pinia).use(router).mount('#app');
updateAppTheme();
