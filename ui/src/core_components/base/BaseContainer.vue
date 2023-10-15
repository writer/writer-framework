<template>
	<div class="containerWrapper" :style="containerWrapperStyle">
		<div class="container" :class="{horizontal: props.horizontal === true}" data-streamsync-container :style="containerStyle">
			<slot></slot>
		</div>
	</div>

</template>

<script setup lang="ts">

import {computed} from "vue";

const props = defineProps<{
	contentWidth: string;
	contentHAlign: string;
	contentPadding: string;
	horizontal?: boolean;
}>();

const containerStyle = computed(() => {
	if (props.horizontal === true) {
		return {
			width: props.contentWidth,
			justifyContent: props.contentHAlign,
			padding: props.contentPadding,
		};
	}

	return {
		width: props.contentWidth,
		alignItems: props.contentHAlign,
		padding: props.contentPadding,
	};
});

const containerWrapperStyle = computed(() => {
	return {
		justifyContent: props.contentHAlign,
	};
});
</script>

<style scoped>
@import "../../renderer/sharedStyles.css";

.containerWrapper {
	display: flex;
}

.container {
	flex-wrap: wrap;
}
</style>