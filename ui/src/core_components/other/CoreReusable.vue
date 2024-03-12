<template>
	<div class="CoreReuse">
		<component :is="vnode" />
	</div>
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
		allowedChildrenTypes: ["inherit"],
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
const renderProxiedComponent = inject(injectionKeys.renderProxiedComponent);
const vnode = ref(h("div", "No component selected"));

function render() {
	if (!fields.parentId.value) {
		vnode.value = h("div", "No component selected");
		return;
	}
	const reusedNode = renderProxiedComponent(fields.parentId.value, 0);
	vnode.value = reusedNode;
}

watch([fields.parentId], render);
render();
</script>

<style scoped>
.CoreReuse {
	width: fit-content;
	height: fit-content;
	position: relative;
}
</style>
