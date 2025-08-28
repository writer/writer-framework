<template>
	<SharedControlBar>
		<template v-if="isJSONObject(data) || isJSONArray(data)">
			<SharedJsonViewerCollapsible
				v-if="isRoot"
				:open="isRootOpen"
				:data="data"
				@toggle="$emit('toggle', { path: [], open: $event })"
				@copy.stop.prevent="onCopyToClipboard(data)"
			>
				<SharedJsonViewerObject
					:data="data"
					:path="path"
					:initial-depth="initialDepth"
					@toggle="$emit('toggle', $event)"
				/>
			</SharedJsonViewerCollapsible>
			<SharedJsonViewerObject
				v-else
				:data="data"
				:path="path"
				:initial-depth="initialDepth"
				@toggle="$emit('toggle', $event)"
				@copy.stop.prevent="onCopyToClipboard(data)"
			/>
		</template>
		<SharedJsonViewerValue v-else-if="isJSONValue(data)" :data="data" />
		<SharedJsonViewerChildrenCounter v-else :data="{}" />

		<template #actions>
			<SharedCopyClipboardButton
				v-if="enableCopyToJson"
				label="Copy JSON"
				:value="dataAsString"
			/>
		</template>
	</SharedControlBar>
</template>

<script lang="ts">
export type JsonValue = string | number | boolean | null;

export type JsonData = JsonValue | { [x: string]: JsonData } | JsonData[];

export type JsonPath = string[];

export type JsonViewerTogglePayload = { path: JsonPath; open: boolean };
</script>

<script setup lang="ts">
/**
 * This component will detect the shape of the JSON and redirect the right dedicated component.
 */
import { PropType, computed } from "vue";
import { useClipboard } from "@vueuse/core";
import {
	isJSONArray,
	isJSONObject,
	isJSONValue,
	jsonViewerToggleEmitDefinition,
} from "./SharedJsonViewer.utils";
import SharedJsonViewerCollapsible from "./SharedJsonViewerCollapsible.vue";
import SharedJsonViewerObject from "./SharedJsonViewerObject.vue";
import SharedJsonViewerValue from "./SharedJsonViewerValue.vue";
import SharedJsonViewerChildrenCounter from "./SharedJsonViewerChildrenCounter.vue";
import SharedControlBar from "../SharedControlBar.vue";
import { defineAsyncComponentWithLoader } from "@/utils/defineAsyncComponentWithLoader";
import { selectionToJson } from "./selectionToJson";

const SharedCopyClipboardButton = defineAsyncComponentWithLoader({
	loader: () => import("@/components/shared/SharedCopyClipboardButton.vue"),
});

const props = defineProps({
	data: {
		type: [
			String,
			Number,
			Boolean,
			Object,
			Array,
			null,
		] as PropType<JsonData>,
		required: true,
	},
	path: {
		type: Array as PropType<JsonPath>,
		default: () => [],
	},
	hideRoot: {
		type: Boolean,
		required: false,
	},
	initialDepth: { type: Number, default: 0 },
	enableCopyToJson: { type: Boolean, required: false },
});

defineEmits({
	toggle: jsonViewerToggleEmitDefinition,
});

const isRoot = computed(() => props.path.length === 0 && !props.hideRoot);
const isRootOpen = computed(
	() => props.initialDepth === -1 || props.initialDepth > 0,
);

function prettyJson(input: unknown, space = 2) {
	if (input === undefined) {
		return JSON.stringify(null);
	}

	try {
		return JSON.stringify(input, null, space);
	} catch {
		return JSON.stringify(null);
	}
}

const dataAsString = computed(() => prettyJson(props.data, 0));

const { copy } = useClipboard();

function onCopyToClipboard(
	arrayOrObject: Record<string, JsonData> | JsonData[],
) {
	const selection = window.getSelection();
	const selectionText = selection?.toString().trim() ?? "";

	const json = selectionText
		? selectionToJson(arrayOrObject, selectionText)
		: arrayOrObject;

	copy(prettyJson(json));
}
</script>
