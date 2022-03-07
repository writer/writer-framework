import { createApp } from "vue"
import App from "./App.vue"
import streamsync from "./streamsync.js"

const app = createApp(App);

app.provide("streamsync", streamsync);

streamsync.init().then(() => {
    streamsync.startSync();
    app.mount("#app");
});