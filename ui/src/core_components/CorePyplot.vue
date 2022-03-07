<template>
	<div class="CorePyplot component" :data-streamsync-id="componentId" v-show="!isPlaceholder">
        <img :src="figure" v-if="figure" />
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
        figure: function () {
            const figure = this.streamsync.getContentValue(this.componentId, "figure");
            return figure;
        },
        isPlaceholder: function () {
            return this.streamsync.components[this.componentId].placeholder;
        }
    }
}
</script>

<style>

</style>
