import { createApp } from "vue";
import { createPinia } from "pinia";
import App from "./App.vue";
import router from "./router";
import { vLazy } from "./composables/useLazyImage";
import "./style.css";

const app = createApp(App);
app.use(createPinia());
app.use(router);
app.directive("lazy", vLazy);
app.mount("#app");
