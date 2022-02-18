import { reactive } from "vue";

export default {

    components: [],
    state: null,
    webSocket: null,
    startTime: null,

    init: async function () {
        const response = await fetch("/api/init");
        const initData = await response.json();

        this.components = initData.components;
        this.state = reactive(initData.state);
    },

    startSync: function () {
        const url = new URL("/api/echo", window.location.href);
        url.protocol = url.protocol.replace("http", "ws");
        this.webSocket = new WebSocket(url.href);

        this.webSocket.onmessage = (wsEvent) => {
            const freshState = JSON.parse(wsEvent.data);
            Object.assign(this.state, freshState);

            const endTime = performance.now();            
			console.log(`Performance ${ endTime - this.startTime } mills`);
        }

        //this.webSocket.onopen = () => {
        //    this.keepAlive();
        //};

        this.webSocket.onclose = () => { this.reconnect() };
    },

    // keepAlive: function () {
    //     this.forward({ type: "keep_alive" });
    //     setTimeout(() => { 
    //         this.keepAlive();
    //     }, 1000);
    // },

    reconnect: function () {
        this.webSocket = null;
        console.log("Disconnected... Will atempt to reconnect");
        this.init().then(() => {
            this.startSync();
        }).catch(() => {
            console.log("Reconnect failed... Will try again");
            setTimeout(() => { this.reconnect(); }, 1000);
        });
    },

    forward: function (event) {
        if (!this.webSocket) return;

        const wsData = {
            type: event.type,
            targetId: event.target?.dataset.streamsyncId,
            value: event.target?.value || null
        };
        //console.log("eventual", wsData);

        this.webSocket.send(JSON.stringify(wsData));
    }

}