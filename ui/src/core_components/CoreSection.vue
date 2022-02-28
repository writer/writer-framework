<template>
	<div class="CoreSection component" :data-streamsync-id="componentId" v-show="!isPlaceholder">
        <h2 v-if="title">{{ title }}</h2>
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
        title: function () {
            return this.streamsync.getContentValue(this.componentId, "title");
        },
        isPlaceholder: function () {
            return this.streamsync.components[this.componentId].placeholder;
        }
    }
}
</script>

<style>

.CoreSection {
	padding: 8px 24px 8px 24px;
    margin-top: 24px;
    margin-bottom: 24px;
	display: block;
    border: 1px solid var(--separator);
    border-radius: 8px;
}

h2 {
    margin-top: 16px;
}

</style>
