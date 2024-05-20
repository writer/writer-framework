<docs lang="md">
    Writer Framework uses Material Symbols to display icons. To include an icon, check https://fonts.google.com/icons, find the icon's id (such as \`arrow_forward\`) and it to your _Icon.
</docs>

<template>
	<div class="icon">
		<span
			v-if="fields.icon.value"
			class="material-symbols-outlined"
			:style="{
				fontSize: `${fields.size.value}px`,
				color: fields.color.value,
			}"
			>{{ fields.icon.value }}</span
		>
	</div>
</template>

<script lang="ts">
import { FieldCategory, FieldType } from "../../writerTypes";
import { cssClasses } from "../../renderer/sharedStyleFields";

export default {
	writer: {
		name: "Icon",
		description: "A component to display an icon",
		category: "Content",
		fields: {
			icon: {
				name: "Icon",
				type: FieldType.Text,
				desc: `A Material Symbols id, such as "arrow_forward".`,
				category: FieldCategory.Style,
				default: "arrow_forward",
			},
			size: {
				name: "Icon size",
				type: FieldType.Number,
				desc: `Icon size in px`,
				category: FieldCategory.Style,
				default: "14",
			},
			color: {
				name: "Icon color",
				type: FieldType.Color,
				category: FieldCategory.Style,
			},
			cssClasses,
		},
		previewField: "icon",
	},
};
</script>

<script setup lang="ts">
import { inject } from "vue";
import injectionKeys from "../../injectionKeys";

const fields = inject(injectionKeys.evaluatedFields);
</script>

<style scoped>
@import "../../renderer/sharedStyles.css";

.icon {
	display: flex;
	align-items: center;
}
</style>
