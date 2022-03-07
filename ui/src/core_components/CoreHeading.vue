<template>
	<div class="CoreHeading component" :data-streamsync-id="componentId" v-show="!isPlaceholder">
        <h1>{{ text }}</h1>
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

<style scoped>

h1 {
    font-size: 1.2rem;
    font-weight: normal;
}

</style>