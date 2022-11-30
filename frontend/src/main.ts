import { createApp } from 'vue'
import Router from './common/Router';
import App from './pages/App.vue'
import './styles/global.scss'

createApp(App).use(Router).mount('#app');
