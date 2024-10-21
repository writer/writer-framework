<template>
	<BaseContainer
		class="CoreHorizontalStack"
		:content-h-align="fields.contentHAlign.value"
		:content-v-align="fields.contentVAlign.value"
		:content-padding="fields.contentPadding.value"
		:is-horizontal="true"
	>
		<slot></slot>
	</BaseContainer>
</template>

<script lang="ts">
import {
	contentHAlign,
	contentVAlign,
	contentPadding,
	cssClasses,
} from "@/renderer/sharedStyleFields";

const description =
	"A layout component that stacks its child components horizontally, wrapping them to the next row if necessary.";

export default {
	writer: {
		name: "Horizontal Stack",
		description,
		allowedChildrenTypes: ["*"],
		category: "Layout",
		fields: {
			contentPadding: {
				...contentPadding,
				default: "0",
			},
			contentHAlign,
			contentVAlign,
			cssClasses,
		},
	},
};
</script>
<script setup lang="ts">
import { inject } from "vue";
import injectionKeys from "@/injectionKeys";
import BaseContainer from "../base/BaseContainer.vue";

const fields = inject(injectionKeys.evaluatedFields);
</script>

<style scoped>
@import "@/renderer/sharedStyles.css";

.CoreHorizontalStack {
	width: 100%;
	flex-wrap: wrap;
}
.CoreHorizontalStack > ::v-deep(*) {
	/* override `width: 100%` of child elements to force horizontal stack */
	width: auto !important;
}
</style>
