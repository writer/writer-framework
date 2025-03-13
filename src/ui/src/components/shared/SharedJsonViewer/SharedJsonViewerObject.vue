<template>
	<div class="SharedJsonViewerObject">
		<template
			v-for="([key, value], index) in Object.entries(data)"
			:key="index"
		>
			<!-- This is a single value, we display it as plain key/value text -->
			<div
				v-if="isJSONValue(value) || getJSONLength(value) === 0"
				class="SharedJsonViewerObject__value"
			>
				<span>{{ key }}</span
				>:
				<SharedJsonViewerValue :data="value" />
			</div>
			<!-- This is a an object -->
			<SharedJsonViewerCollapsible
				v-else
				:open="isOpen(key)"
				:title="key"
				:data="value"
				@toggle="toggleOpenedKey(key, $event)"
			>
				<SharedJsonViewer
					v-if="isOpen(key)"
					:data="value"
					:path="[...path, key]"
					:initial-depth="initialDepth"
					@toggle="$emit('toggle', $event)"
				/>
			</SharedJsonViewerCollapsible>
		</template>
	</div>
</template>

<script setup lang="ts">
import { PropType, computed, ref, toRef, watch } from "vue";
import {
	getJSONLength,
	isJSONValue,
	jsonViewerToggleEmitDefinition,
} from "./SharedJsonViewer.utils";
import type { JsonData, JsonPath } from "./SharedJsonViewer.vue";
import SharedJsonViewer from "./SharedJsonViewer.vue";
import SharedJsonViewerCollapsible from "./SharedJsonViewerCollapsible.vue";
import SharedJsonViewerValue from "./SharedJsonViewerValue.vue";

const props = defineProps({
	data: {
		type: [Object, Array] as PropType<JsonData>,
		required: true,
	},
	path: {
		type: Array as PropType<JsonPath>,
		default: () => [],
	},
	initialDepth: { type: Number, default: 0 },
});

const initialDepth = toRef(props, "initialDepth");

const emit = defineEmits({
	toggle: jsonViewerToggleEmitDefinition,
});

const openedKeys = ref<string[]>([]);

const currentLevel = computed(() => props.path.length + 1);

watch(
	initialDepth,
	() => {
		if (initialDepth.value === 0) {
			openedKeys.value = [];
			return;
		}

		const shouldAddKeys =
			initialDepth.value === -1 ||
			initialDepth.value > currentLevel.value;

		if (!shouldAddKeys) return;

		const keysToOpen = new Set([
			...openedKeys.value,
			...Object.keys(props.data),
		]);

		openedKeys.value = Array.from(keysToOpen);
	},
	{ immediate: true },
);

function toggleOpenedKey(key: string, open: boolean) {
	if (open) {
		openedKeys.value = [...openedKeys.value, key];
	} else {
		openedKeys.value = openedKeys.value.filter((k) => k !== key);
	}
	emit("toggle", { open, path: [...props.path, key] });
}

function isOpen(key: string) {
	return openedKeys.value.includes(String(key));
}
</script>

<style scoped>
.SharedJsonViewerObject {
	display: flex;
	flex-direction: column;
	gap: 4px;
}

.SharedJsonViewerObject__value {
	font-family: monospace;
	font-size: 12px;
	padding-left: 24px;

	display: flex;
	gap: 4px;
}
</style>
