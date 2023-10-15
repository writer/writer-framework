<template>
	<BaseContainer :contentWidth=fields.contentWidth.value
								 :contentHAlign=fields.contentHAlign.value
								 :contentPadding=fields.contentPadding.value
								 :horizontal=true>
		<slot></slot>
	</BaseContainer>
</template>

<script lang="ts">
import {contentHAlign, contentPadding, contentWidth, cssClasses} from "../renderer/sharedStyleFields";

const description =
	"A layout component that stacks its child components horizontally, wrapping them to the next row if necessary.";

export default {
	streamsync: {
		name: "Horizontal Stack",
		description,
		allowedChildrenTypes: ["*"],
		category: "Layout",
		fields: {
			contentPadding,
			contentWidth,
			contentHAlign,
			cssClasses,
		},
	},
};
</script>
<script setup lang="ts">
import {computed, inject} from "vue";
import injectionKeys from "../injectionKeys";
import {contentWidth} from "../renderer/sharedStyleFields";
import BaseContainer from "./base/BaseContainer.vue";

const fields = inject(injectionKeys.evaluatedFields);

</script>

<style scoped>
@import "../renderer/sharedStyles.css";

</style>
