<template>
	<div class="BubbleMessage">
		<div class="triangle"></div>
		<div class="message">
			<!-- Shows the current value of the field "text" -->

			{{ fields.text.value }}
		</div>
	</div>
</template>

<script lang="ts">
export default {
	writer: {
		name: "Bubble Message",
		description: "Shows a message in the shape of a speech bubble.",
		category: "Content",

		// Fields will be editable via Writer Framework Builder

		fields: {
			text: {
				name: "Text",
				type: FieldType.Text,
			},
		},

		// Preview field is used in the Component Tree

		previewField: "text",
	},
};
</script>
<script setup lang="ts">
import { FieldType } from "@/writerTypes";
import injectionKeys from "@/injectionKeys";
import { inject } from "vue";

/*
The values for the fields defined earlier in the custom option
will be available using the evaluatedFields injection symbol.
*/

const fields = inject(injectionKeys.evaluatedFields);
</script>

<style scoped>
.BubbleMessage {
	width: fit-content;
	max-width: 100%;
	display: flex;
	position: relative;
	background: white;
}

.triangle {
	flex: 0 0 auto;
	border-left: 12px solid white;
	border-top: 12px solid var(--wdsColorGray1);
}

.message {
	flex: 1 0 auto;
	background: var(--wdsColorGray1);
	border-radius: 0 12px 12px 12px;
	padding: 16px;
}
</style>
