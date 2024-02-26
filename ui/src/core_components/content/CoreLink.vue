<template>
	<div class="CoreLink">
		<a
			:href="fields.url.value"
			:target="fields.target.value"
			:rel="fields.rel.value"
		>
			{{ displayText }}
		</a>
	</div>
</template>

<script lang="ts">
import { FieldType } from "../../streamsyncTypes";
import { cssClasses, primaryTextColor } from "../../renderer/sharedStyleFields";
import injectionKeys from "../../injectionKeys";
let options = [];

export default {
	streamsync: {
		name: "Link",
		description: "A component to create a hyperlink.",
		category: "Content",
		fields: {
			url: {
				name: "URL",
				type: FieldType.Text,
				desc: "A valid URL.",
				options: () => Object.fromEntries(options.value),
			},
			target: {
				name: "Target",
				type: FieldType.Text,
				options: {
					_self: "Self",
					_blank: "Blank",
					_parent: "Parent",
					_top: "Top",
				},
				desc: "Specifies where to open the linked document.",
				default: "_self",
			},
			rel: {
				name: "Rel",
				type: FieldType.Text,
				desc: "Specifies the relationship between the current document and the linked document.",
			},
			text: {
				name: "Text",
				default: "",
				type: FieldType.Text,
				desc: "The text to display in the link.",
			},
			primaryTextColor,
			cssClasses,
		},
	},
};
</script>

<script setup lang="ts">
import { inject, computed } from "vue";
const ss = inject(injectionKeys.core);
const fields = inject(injectionKeys.evaluatedFields);

options = computed(() => {
	return ss
		.getComponents("root", true)
		.map((page) => page.content.key)
		.filter((key) => Boolean(key))
		.map((key) => [`#${key}`, key]);
});

const displayText = computed(() => {
	return fields.text.value || fields.url.value || "Link";
});
</script>

<style scoped>
.CoreLink a {
	color: var(--primaryTextColor);
}
.CoreLink.beingEdited:not(.selected) a {
	pointer-events: none;
}
</style>
