<template>
	<section class="CoreSection">
		<h3 v-if="fields.title.value">{{ fields.title.value }}</h3>
		<BaseContainer
			:content-h-align="fields.contentHAlign.value"
			:content-padding="fields.contentPadding.value"
		>
			<slot></slot>
		</BaseContainer>
	</section>
</template>

<script lang="ts">
import { FieldType } from "@/writerTypes";
import {
	accentColor,
	primaryTextColor,
	secondaryTextColor,
	containerBackgroundColor,
	containerShadow,
	separatorColor,
	buttonColor,
	buttonTextColor,
	buttonShadow,
	cssClasses,
	contentHAlign,
	contentPadding,
} from "@/renderer/sharedStyleFields";

const description =
	"A container component that divides the layout into sections, with an optional title.";

export default {
	writer: {
		name: "Section",
		description,
		category: "Layout",
		allowedChildrenTypes: ["*"],
		fields: {
			title: {
				name: "Title",
				init: "Section Title",
				desc: "Leave blank to hide.",
				type: FieldType.Text,
			},
			accentColor,
			primaryTextColor,
			secondaryTextColor,
			containerBackgroundColor,
			containerShadow,
			separatorColor,
			buttonColor,
			buttonTextColor,
			buttonShadow,
			contentPadding: {
				...contentPadding,
				default: "16px",
			},
			contentHAlign,
			cssClasses,
		},
		previewField: "title",
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
.CoreSection {
	border: 1px solid var(--separatorColor);
	border-radius: 8px;
	box-shadow: var(--containerShadow);
	background-color: var(--containerBackgroundColor);
}

h3 {
	margin: 16px 16px 0 16px;
}
</style>
