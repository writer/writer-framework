<template>
	<SharedControlBar>
		<template v-if="isJSONObject(data) || isJSONArray(data)">
			<SharedJsonViewerCollapsible
				v-if="isRoot"
				:open="isRootOpen"
				:data="data"
				@toggle="$emit('toggle', { path: [], open: $event })"
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
const dataAsString = computed(() => {
	if (props.data === undefined) return JSON.stringify(null);
	return JSON.stringify(props.data);
});
</script>
