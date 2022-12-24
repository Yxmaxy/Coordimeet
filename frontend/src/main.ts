import { createPinia } from 'pinia';
import { createApp } from 'vue'
import Router from './common/Router';
import App from './pages/App.vue'
import './styles/global.scss'

const pinia = createPinia();

createApp(App).use(pinia).use(Router).mount('#app');
