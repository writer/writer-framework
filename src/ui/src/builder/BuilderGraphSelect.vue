<script setup lang="ts">
import injectionKeys from "@/injectionKeys";
import {
	computed,
	defineAsyncComponent,
	inject,
	onMounted,
	PropType,
} from "vue";
import { useListResources } from "@/composables/useListResources";
import type { Option } from "./BuilderSelect.vue";
import BuilderAsyncLoader from "./BuilderAsyncLoader.vue";
import type { WriterGraph } from "@/writerTypes";
import WdsTextInput from "@/wds/WdsTextInput.vue";

const BuilderSelect = defineAsyncComponent({
	loader: () => import("./BuilderSelect.vue"),
	loadingComponent: BuilderAsyncLoader,
});

const wf = inject(injectionKeys.core);

defineProps({
	enableMultiSelection: { type: Boolean, required: false },
});

const currentValue = defineModel({
	type: [String, Array] as PropType<string | string[]>,
	required: true,
});

const {
	load: loadGraphs,
	data: graphs,
	isLoading,
} = useListResources<WriterGraph>(wf, "graphs");

onMounted(loadGraphs);

const options = computed(() =>
	graphs.value
		.map<Option>((graph) => ({
			label: graph.name,
			detail: graph.description,
			value: graph.id,
		}))
		.sort((a, b) => a.label.localeCompare(b.label)),
);

const currentValueStr = computed<string>({
	get() {
		if (currentValue.value === undefined) return "";

		return typeof currentValue.value === "string"
			? currentValue.value
			: currentValue.value.join(",");
	},
	set(value: string) {
		currentValue.value = value.split(",");
	},
});

const selectedData = computed(() => {
	if (currentValue.value === undefined) return undefined;

	return typeof currentValue.value === "string"
		? graphs.value.find((g) => g.id === currentValue.value)
		: graphs.value.filter((g) => currentValue.value.includes(g.id));
});

defineExpose({ selectedData });
</script>

<template>
	<div class="BuilderGraphSelect--text">
		<BuilderSelect
			v-if="graphs.length > 0 || isLoading"
			v-model="currentValue"
			:options="options"
			hide-icons
			enable-search
			:loading="isLoading"
			:enable-multi-selection="enableMultiSelection"
		/>
		<WdsTextInput v-else v-model="currentValueStr" />
	</div>
</template>

<style scoped>
.BuilderGraphSelect--text {
	width: 100%;
	display: flex;
	gap: 12px;
	align-items: center;
}
</style>
