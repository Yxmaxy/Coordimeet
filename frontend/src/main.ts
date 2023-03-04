import { createPinia } from 'pinia';
import { createApp } from 'vue'
import router from './common/router';
import App from './pages/App.vue'
import './styles/global.scss'

const pinia = createPinia();

createApp(App).use(pinia).use(router).mount('#app');
