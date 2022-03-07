import { createApp, reactive } from "vue";
import templateMapping from "./templateMapping.js";

export default {

    components: null,
    initialState: null,
    state: null,
    webSocket: null,
    startTime: null,

    // Set up components and state

    init: async function () {
        const response = await fetch("/api/init");
        const initData = await response.json();    

        this.components = reactive(initData.components);
        this.initialState = { ...initData.state }; // A copy of the initial state is kept to reset it in case of disconnection
        this.state = reactive(initData.state);
    },

    // Open and setup websocket

    startSync: function () {
        const url = new URL("/api/echo", window.location.href);
        url.protocol = url.protocol.replace("http", "ws");
        this.webSocket = new WebSocket(url.href);

        this.webSocket.onmessage = (wsEvent) => {
            const data = JSON.parse(wsEvent.data);
            const mutations = data.mutations;
            const components = data.components;
            
            Object.assign(this.state, mutations); // Ingest mutations coming from the server
            Object.keys(this.components).forEach(key => {
                if (components[key] === undefined) {
                    delete this.components[key];
                }
            });

            Object.assign(this.components, components);
        };

        this.webSocket.onclose = () => { this.reconnect(); };
    },

    reconnect: async function () {
        const reconnectDelay = 1000; // Delay for retrying (in ms)
        this.webSocket = null;
        console.log("Disconnected... Will atempt to reconnect");
        
        try {
            Object.assign(this.state, this.initialState); // Reset to initial state
            this.startSync(); // Attempt to reopen websocket
        } catch (e) {
            console.log("Reconnect failed... Will try again");
            setTimeout(() => { this.reconnect(); }, reconnectDelay);
        }        
    },

    // Get content value, evaluating references to state.
    // For example, "Pet: @animal" will be evaluated as "Pet: dog" if the state contains a key "animal" with value "dog".  
    // Called by rendered components to populate themselves.

    getContentValue: function (componentId, key) {
        const component = this.components[componentId];
        if (!component.content) return null;
        const expr = component.content[key];
        if (expr === undefined || expr === null) return null;

        if (isNaN(expr) === false) return expr; // If it's a number, don't attempt to look for references to state 
        
        // Look for state references (marked by @) and replace them by state values

        // monoMatch: If the expression only contains a state reference, return the latter, rather than a string.
        // This prevents references to null state values to be converted into strings with the value "null".
        // For example, if state["a"] = null: "@a" will evaluate to null. "value is @a" will evaluate to "value is null".
        let monoMatch; 

        const evaluatedExpr = expr.replace(/[\\]?@([\w]*)/g, (match, p1) => {
            if (match.charAt(0) == "\\") return match.substring(1); // Escaped @, don't evaluate, return without \
            if (!p1 || this.state[p1] === undefined) return;

            if (expr === match) { // The whole expression consists of a single reference
                monoMatch = this.state[p1];
                return;
            }

            return this.state[p1]
        });

        const value = monoMatch === undefined ? evaluatedExpr : monoMatch;
        return value;
    },

    // Forward event via websocket

    forward: function (event) {
        if (!this.webSocket) return;

        const wsData = {
            type: event.type,
            targetId: event.target?.closest("[data-streamsync-id]").dataset.streamsyncId,
            value: event.target?.value || null
        };

        this.webSocket.send(JSON.stringify(wsData));
    },

    // Attach event listeners for which the component has handlers

    addEventListeners: function (componentId, element) {
        const component = this.components[componentId];
        if (!component.handlers) return;

        Object.keys(component.handlers).forEach(eventType => {
            element.addEventListener(eventType, event => { 
                this.forward(event);
            });
        });
    },

    // Render and mount all registered components to a target element
    // If no parentComponentId is specified, the root components are rendered.
    // If a parentComponentId is specified, the children components of such component are rendered.
    
    mountComponents: function (target, parentComponentId = null) {
        Object.entries(this.components).forEach(([componentId, component]) => {
            if (component.container !== parentComponentId) return;

            const renderedComponent = this.renderComponent(componentId, component);
            if (!renderedComponent) return;
            target.appendChild(renderedComponent);
        });
    },

    // Renders a Vue component from a Streamsync definition

    renderComponent: function (componentId, component) {
        const template = templateMapping[component.type];
        if (!template) return; // Unmapped type
        const wrapper = document.createElement("span");
        const subApp = createApp(template, { componentId, isPlaceholder: component.placeholder });
        subApp.provide("streamsync", this);
        subApp.mount(wrapper);
        return wrapper;
    }
}