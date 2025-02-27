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
import type { WriterApplication } from "@/writerTypes";
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
} = useListResources<WriterApplication>(wf, "applications");

onMounted(loadGraphs);

function getAppType(app: WriterApplication) {
	switch (app.type) {
		case "chat":
			return "Chat app";
		case "framework":
			return "Framework";
		case "generation":
			return "Text generation";
		case "research":
			return "Research assistant";
	}
}

const options = computed(() =>
	graphs.value
		.map<Option>((app) => ({
			label: app.name,
			value: app.id,
			detail: [getAppType(app), app.status].join(` · `),
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
