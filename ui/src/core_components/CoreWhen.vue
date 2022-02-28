<template>
	<div class="CoreWhen component" :data-streamsync-id="componentId" v-show="!isPlaceholder">
        <div ref="container">
        </div>
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
        this.streamsync.mountComponents(this.$refs.container, this.componentId);
    },
    computed: {
        isPlaceholder: function () {
            return this.streamsync.components[this.componentId].placeholder;
        }
    }
}
</script>

<style>

.CoreWhen {
}

</style>
