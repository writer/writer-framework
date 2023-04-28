<template>
	<div class="CoreHeading" :style="{ 'text-align': fields.alignment }">
		<h1 v-if="fields.headingType == 'h1'">{{ fields.text }}</h1>
		<h3 v-else-if="fields.headingType == 'h3'">{{ fields.text }}</h3>
		<h4 v-else-if="fields.headingType == 'h4'">{{ fields.text }}</h4>
		<h2 v-else>{{ fields.text }}</h2>
	</div>
</template>

<script lang="ts">
const description =
	"A text component used to display headings or titles in different sizes and styles.";

export default {
	streamsync: {
		name: "Heading",
		description,
		category: "Content",
		fields: {
			text: {
				name: "Text",
				default: "(No text)",
				init: "Heading Text",
				type: FieldType.Text,
			},
			headingType: {
				name: "Heading type",
				default: "h2",
				options: {
					h1: "h1 (Big)",
					h2: "h2 (Normal)",
					h3: "h3 (Small)",
					h4: "h4 (Smallest)",
				},
				type: FieldType.Text,
				category: FieldCategory.Style,
			},
			alignment: {
				name: "Alignment",
				default: "left",
				type: FieldType.Text,
				category: FieldCategory.Style,
				options: {
					left: "Left",
					center: "Center",
					right: "Right",
				},
			},
			primaryTextColor,
		},
		previewField: "text",
	},
};
</script>
<script setup lang="ts">
import { inject } from "vue";
import { FieldCategory, FieldType } from "../streamsyncTypes";
import injectionKeys from "../injectionKeys";
import { primaryTextColor } from "../renderer/sharedStyleFields";
const fields = inject(injectionKeys.evaluatedFields);
</script>
<style scoped>
@import "../renderer/sharedStyles.css";

.CoreHeading {
	color: var(--primaryTextColor);
}
</style>
