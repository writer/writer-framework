<script setup lang="ts">
import injectionKeys from "@/injectionKeys";
import { computed, inject, onMounted, PropType } from "vue";
import { useListResources } from "@/composables/useListResources";
import type { Option } from "@/wds/WdsSelect.vue";
import type { WriterModel } from "@/writerTypes";
import WdsTextInput from "@/wds/WdsTextInput.vue";
import { defineAsyncComponentWithLoader } from "@/utils/defineAsyncComponentWithLoader";

const WdsSelect = defineAsyncComponentWithLoader({
	loader: () => import("@/wds/WdsSelect.vue"),
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
	load: loadModels,
	data: models,
	isLoading,
} = useListResources<WriterModel>(wf, "models");

onMounted(loadModels);

const options = computed(() =>
	models.value
		.map<Option>((model) => ({
			label: model.name,
			value: model.id,
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
		? models.value.find((m) => m.id === currentValue.value)
		: models.value.filter((m) => currentValue.value.includes(m.id));
});

defineExpose({ selectedData });
</script>

<template>
	<div class="BuilderModelSelect--text">
		<WdsSelect
			v-if="models.length > 0 || isLoading"
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
