<template>
	<BaseEmptiness
		class="ChildlessPlaceholder"
		:component-id="componentId"
		:message="message"
	/>
</template>

<script setup lang="ts">
import { computed, inject } from "vue";
import BaseEmptiness from "../core_components/base/BaseEmptiness.vue";
import injectionKeys from "../injectionKeys";
import { Component } from "../writerTypes";

const ALLOWED_LIST_MAX_LENGTH = 10;
const wf = inject(injectionKeys.core);

const props = defineProps({
	componentId: { type: String, required: true },
});

const typesToMessage = (
	types: Component["type"][],
	lastJoiner: "or" | "and",
) => {
	const definitions = types.map((type) => wf.getComponentDefinition(type));
	const names = definitions.map((def) => def?.name);
	const message = `${names.slice(0, -1).join(", ")} ${
		names.length > 1 ? lastJoiner : ""
	} ${names.at(-1)}`;
	return message;
};

const message = computed(() => {
	const containableTypes = wf.getContainableTypes(props.componentId);
	let message: string;

	if (containableTypes.length <= ALLOWED_LIST_MAX_LENGTH) {
		const typesMessage = typesToMessage(containableTypes, "and");
		message = `You can add ${typesMessage} components`;
	}

	return message;
});
</script>
