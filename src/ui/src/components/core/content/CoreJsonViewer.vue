<template>
	<div class="CoreJsonViewer">
		<SharedJsonViewer
			:data="data ?? {}"
			:initial-depth="initialDepth"
			:enable-copy-to-json="fields.copy.value"
			:hide-root="fields.hideRoot.value"
		/>
	</div>
</template>

<script lang="ts">
import {
	baseYesNoField,
	cssClasses,
	secondaryTextColor,
	separatorColor,
} from "@/renderer/sharedStyleFields";
import {
	FieldCategory,
	FieldType,
	WriterComponentDefinition,
} from "@/writerTypes";
import {
	validatorCssSize,
	validatorPositiveNumber,
} from "@/constants/validators";

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
			validator: validatorPositiveNumber,
		},
		hideRoot: {
			...baseYesNoField,
			name: "Hide root",
			desc: "Don't show the type of the root node when it's an Object or an Array.",
			default: "no",
			category: FieldCategory.Style,
		},
		copy: {
			...baseYesNoField,
			name: "Copy",
			desc: "If active, adds a control bar with copy JSON button.",
			default: "no",
			category: FieldCategory.Style,
		},
		jsonViewerIndentationSpacing: {
			name: "JSON indentation",
			type: FieldType.Width,
			category: FieldCategory.Style,
			applyStyleVariable: true,
			validator: validatorCssSize,
		},
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
import type { JsonData } from "@/components/shared/SharedJsonViewer/SharedJsonViewer.vue";
import SharedJsonViewer from "@/components/shared/SharedJsonViewer/SharedJsonViewer.vue";

const fields = inject(injectionKeys.evaluatedFields);

const data = computed(() => fields.data.value as JsonData);

const initialDepth = computed(() => Number(fields.initialDepth.value) || 0);
</script>
