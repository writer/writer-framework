<template>
	<div class="BuilderFieldsHandler" :data-automation-key="props.fieldKey">
		<WdsSelect v-model="selectedHandler" :options="options" />
	</div>
</template>

<script setup lang="ts">
import { inject, computed, defineAsyncComponent, toRef } from "vue";
import { useComponentFieldViewModel } from "../useComponentFieldViewModel";
import injectionKeys from "@/injectionKeys";
import { Option } from "@/wds/WdsSelect.vue";

const WdsSelect = defineAsyncComponent(() => import("@/wds/WdsSelect.vue"));

const wf = inject(injectionKeys.core);

const props = defineProps({
	componentId: { type: String, required: true },
	fieldKey: { type: String, required: true },
});

const selectedHandler = useComponentFieldViewModel({
	componentId: toRef(props, "componentId"),
	fieldKey: toRef(props, "fieldKey"),
	defaultValue: "",
});

const options = computed<Option[]>(() => {
	const blueprintsOptions = wf.userFunctions.value
		.map((f) => f.name)
		.sort((a, b) => a.localeCompare(b))
		.map((key) => ({
			value: key,
			label: key,
			icon: "wds-function",
		}));

	const options: Option[] = [
		{ value: "", label: "(No handler)", icon: "ban" },
		...blueprintsOptions,
	];

	// add an option if selected blueprint does not exists
	if (!options.some((o) => o.value === selectedHandler.value)) {
		const key = selectedHandler.value;
		options.push({ value: key, label: key });
	}

	return options;
});
</script>
