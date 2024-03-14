<template>
	<component :is="vnode" />
</template>

<script lang="ts">
import { FieldType } from "../../streamsyncTypes";
import { h, inject, watch, ref } from "vue";
import injectionKeys from "../../injectionKeys";

export default {
	streamsync: {
		name: "Reuse Component",
		description:
			"Those components are used to reuse other components. " +
			"Reused components share the same state and are updated together.",
		category: "Other",
		allowedChildrenTypes: [],
		fields: {
			parentId: {
				name: "Component id",
				type: FieldType.Text,
				desc: "The id of the component to reuse.",
			},
		},
	},
};
</script>
<script setup lang="ts">
const fields = inject(injectionKeys.evaluatedFields);
const ss = inject(injectionKeys.core);
const renderProxiedComponent = inject(injectionKeys.renderProxiedComponent);
const isBeingEdited = inject(injectionKeys.isBeingEdited);
const componentId = inject(injectionKeys.componentId);
const vnode = ref(h("div", ""));
const def = ss.getComponentDefinitionById(fields.parentId);

function renderError(message: string) {
	vnode.value = h("div", isBeingEdited.value ? message : "");
}

function render() {
	if (!fields.parentId.value) {
		renderError("No component selected to reuse");
		return;
	}
	if (componentId === fields.parentId.value || !def.value) {
		renderError("The id specified for reuse doesn't match any component.");
		return;
	}
	ss.setComponentDefinitionById(componentId, {
		slot: def.value.slot,
		positionless: def.value.positionless,
	});
	const reusedNode = renderProxiedComponent(fields.parentId.value, 0);
	vnode.value = reusedNode;
}

watch([fields.parentId, def], render, { immediate: true });
</script>
