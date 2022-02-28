<template>
	<button class="CoreButton component" :data-streamsync-id="componentId" v-show="!isPlaceholder">
        <slot>{{ text }}</slot>
    </button>
</template>

<script>
export default {
    inject: [ "streamsync" ],
	props: {
        componentId: String
    },
    mounted: function () {
        this.streamsync.addEventListeners(this.componentId, this.$el);
    },
    computed: {
        text: function () {
            return this.streamsync.getContentValue(this.componentId, "text");
        },
        isPlaceholder: function () {
            return this.streamsync.components[this.componentId].placeholder;
        }
    }
}
</script>

<style>

button {
    font-size: 0.8rem;
    border-radius: 8px;
    border: 1px solid var(--separator);
    padding: 8px;
    background: #f0f0f0;
    display: block;
}

button:hover {
    background: #e0e0e0;
}

</style>
