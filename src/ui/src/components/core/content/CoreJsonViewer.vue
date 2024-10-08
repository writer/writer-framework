<template>
	<div class="CoreJsonViewer">
		<BaseJsonViewer
			v-if="data"
			:data="data"
			:initial-depth="initialDepth"
		/>
		<BaseJsonViewerChildrenCounter v-else :data="{}" />
	</div>
</template>

<script lang="ts">
import {
	accentColor,
	cssClasses,
	secondaryTextColor,
	separatorColor,
} from "@/renderer/sharedStyleFields";
import {
	FieldCategory,
	FieldType,
	WriterComponentDefinition,
} from "@/writerTypes";

const description = "A component to explore JSON data as a hierarchy.";

const initialData = {
	name: "JSON Viewer",
	description: "A JSON tree viewer where you can expand the keys.",
	sample: {
		description: "This sample is opened by default",
		bool: true,
		null: null,
		list: [1, "two", { key: 3 }],
	},
	sampleClosed: {
		description: "This sample is not opened by default",
	},
	createdAt: new Date(),
};

const definition: WriterComponentDefinition = {
	name: "JSON Viewer",
	description,
	category: "Content",
	fields: {
		data: {
			name: "Data",
			init: JSON.stringify(initialData),
			type: FieldType.Object,
		},
		initialDepth: {
			name: "Initial depth",
			desc: "Sets the initial viewing depth of the JSON tree hierarchy. Use -1 to display the full hierarchy.",
			type: FieldType.Number,
			init: "0",
		},
		jsonViewerIndentationSpacing: {
			name: "JSON indentation",
			type: FieldType.Width,
			category: FieldCategory.Style,
			applyStyleVariable: true,
		},
		accentColor,
		secondaryTextColor,
		separatorColor,
		cssClasses,
	},
	previewField: "data",
};

export default { writer: definition };
</script>

<script setup lang="ts">
import { computed, inject } from "vue";
import injectionKeys from "@/injectionKeys";
import type { JsonData } from "../base/BaseJsonViewer.vue";
import BaseJsonViewer from "../base/BaseJsonViewer.vue";
import BaseJsonViewerChildrenCounter from "../base/BaseJsonViewerChildrenCounter.vue";

const fields = inject(injectionKeys.evaluatedFields);

const data = computed(() => fields.data.value as JsonData);

const initialDepth = computed(() => Number(fields.initialDepth.value) || 0);
</script>

<style scoped>
.error {
	color: #ffcfc2;
}
</style>
