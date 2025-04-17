<template>
	<div class="BuilderFieldsHandler" :data-automation-key="props.fieldKey">
		<WdsSelect v-model="selectedHandler" :options="options" />
	</div>
</template>

<script setup lang="ts">
import { toRefs, inject, computed, defineAsyncComponent } from "vue";
import { useComponentActions } from "../useComponentActions";
import injectionKeys from "@/injectionKeys";
import { Option } from "@/wds/WdsSelect.vue";

const WdsSelect = defineAsyncComponent(() => import("@/wds/WdsSelect.vue"));

const wf = inject(injectionKeys.core);
const ssbm = inject(injectionKeys.builderManager);
const { setContentValue } = useComponentActions(wf, ssbm);

const props = defineProps({
	componentId: { type: String, required: true },
	fieldKey: { type: String, required: true },
});

const { componentId, fieldKey } = toRefs(props);
const component = computed(() => wf.getComponentById(componentId.value));

const selectedHandler = computed<string>({
	get: () => component.value?.content[props.fieldKey] ?? "",
	set: (key) => setContentValue(component.value.id, fieldKey.value, key),
});

const options = computed<Option[]>(() => {
	const blueprintsOptions = wf.userFunctions.value
		.map((f) => f.name)
		.sort((a, b) => a.localeCompare(b))
		.map((key) => ({
			value: key,
			label: key,
			icon: "function",
		}));

	const options: Option[] = [
		{ value: "", label: "(No handler)", icon: "block" },
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
