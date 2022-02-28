<template>
	<div class="CoreText component" :data-streamsync-id="componentId" v-show="!isPlaceholder">
        <slot>{{ text }}</slot>
    </div>
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

.CoreText {
    font-size: 0.8rem;
    white-space: pre-wrap;
}

</style>
