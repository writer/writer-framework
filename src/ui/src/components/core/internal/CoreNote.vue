<template>
	<BaseNote
		v-if="shouldDiplay"
		:component-id="componentId"
		class="CoreComment"
	/>
</template>

<script lang="ts">
import BaseNote from "@/components/core/base/BaseNote.vue";
import {
	FieldControl,
	FieldType,
	WriterComponentDefinition,
} from "@/writerTypes";

const description = "TODO";

const definition: WriterComponentDefinition = {
	name: "Note",
	description,
	category: "Internal",
	fields: {
		content: {
			name: "Content",
			type: FieldType.Text,
			control: FieldControl.Textarea,
		},
		createdAt: {
			name: "Created At",
			type: FieldType.Text,
		},
		createdBy: {
			name: "Created By",
			type: FieldType.Number,
		},
	},
};

export default {
	writer: definition,
};
</script>
<script setup lang="ts">
import { computed, inject } from "vue";
import injectionKeys from "@/injectionKeys";

const wf = inject(injectionKeys.core);
const wfbm = inject(injectionKeys.builderManager);
const componentId = inject(injectionKeys.componentId);

const shouldDiplay = computed(
	() => wf.mode.value === "edit" && wfbm.mode.value !== "preview",
);
</script>

<style scoped>
@import "@/renderer/sharedStyles.css";
@import "@/renderer/colorTransformations.css";

.CoreComment {
	position: absolute !important;
	top: -32px;
	left: 0px;
}
</style>
