import { createApp } from 'vue';
import { createPinia } from 'pinia';
import veProgress from "vue-ellipse-progress";

import App from './App.vue';
import router from './router';

// Import Bootstrap
import 'bootstrap/dist/css/bootstrap.min.css';
import 'bootstrap';

// Import your custom global styles
import './assets/main.css';

const app = createApp(App);

app.use(createPinia());
app.use(veProgress)
app.use(router);

app.mount('#app');