<template>
	<section class="CoreSection">
		<h2 v-if="fields.title.value">{{ fields.title.value }}</h2>
		<div class="container-wrapper" >
			<div class="container" data-streamsync-container :style="containerStyle">
				<slot></slot>
			</div>
		</div>
	</section>
</template>

<script lang="ts">
import { FieldCategory, FieldType } from "../streamsyncTypes";
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
	cssClasses, contentWidth
} from "../renderer/sharedStyleFields";

const description =
	"A container component that divides the layout into sections, with an optional title.";

export default {
	streamsync: {
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
			contentWidth,
			cssClasses,
		},
		previewField: "title",
	},
};
</script>
<script setup lang="ts">
import {computed, inject} from "vue";
import injectionKeys from "../injectionKeys";

const fields = inject(injectionKeys.evaluatedFields);

const containerStyle = computed(() => {
	return {
		width: fields.contentWidth.value,
	};
});
</script>

<style scoped>
@import "../renderer/sharedStyles.css";
.CoreSection {
	padding: 16px;
	border: 1px solid var(--separatorColor);
	border-radius: 8px;
	box-shadow: var(--containerShadow);
	background-color: var(--containerBackgroundColor);
}

h2 {
	margin-bottom: 16px;
}
</style>
