<template>
	<component :is="vnode" v-if="shouldRender" />
</template>

<script lang="ts">
import { FieldType } from "@/writerTypes";
import { computed, defineProps, h, inject, ref, watch } from "vue";
import injectionKeys from "@/injectionKeys";

export default {
	writer: {
		name: "Reuse Component",
		slot: "*",
		description:
			"Those components are used to reuse other components. " +
			"Reused components share the same state and are updated together.",
		category: "Other",
		allowedChildrenTypes: [],
		fields: {
			proxyId: {
				name: "Component id",
				type: FieldType.Text,
				desc: "The id of the component to reuse.",
			},
		},
	},
};
</script>
<script setup lang="ts">
const props = defineProps<{
	contextSlot: string;
}>();
const fields = inject(injectionKeys.evaluatedFields);
const instancePath = inject(injectionKeys.instancePath);
const parentId = instancePath.at(-2).componentId;
const wf = inject(injectionKeys.core);
const renderProxiedComponent = inject(injectionKeys.renderProxiedComponent);
const isBeingEdited = inject(injectionKeys.isBeingEdited);
const componentId = inject(injectionKeys.componentId);
const vnode = ref(h("div", ""));
const shouldRender = ref(true);
const proxyType = computed(
	() => wf.getComponentById(fields.proxyId.value)?.type,
);
const parentType = computed(() => wf.getComponentById(parentId)?.type);

const proxyDefinition = computed(() =>
	proxyType.value ? wf.getComponentDefinition(proxyType.value) : null,
);
const parentDef = computed(() => wf.getComponentDefinition(parentType.value));

function renderError(message: string, cls: string) {
	shouldRender.value = props.contextSlot === "default";
	vnode.value = h(
		"div",
		{ class: ["CoreReuse", cls] },
		isBeingEdited.value ? message : "",
	);
}

function isAllowedChildType(type) {
	return (
		parentDef.value.allowedChildrenTypes?.includes(type) ||
		parentDef.value.allowedChildrenTypes?.includes("*")
	);
}

function isAllowedParentType(type) {
	return (
		!proxyDefinition.value.allowedParentTypes ||
		proxyDefinition.value.allowedParentTypes?.includes(type)
	);
}

function render() {
	if (!fields.proxyId.value) {
		return renderError("No component selected to reuse", "empty");
	}
	if (componentId === fields.proxyId.value || !proxyDefinition.value) {
		return renderError(
			"The id specified for reuse doesn't match any component.",
			"invalid-value",
		);
	}

	if (
		!isAllowedChildType(proxyType.value) ||
		!isAllowedParentType(parentType.value)
	) {
		return renderError(
			`The component cannot be reused here.`,
			"invalid-context",
		);
	}

	shouldRender.value =
		props.contextSlot === (proxyDefinition.value.slot ?? "default");
	const reusedNode = renderProxiedComponent(fields.proxyId.value, 0, {
		class: ["CoreReuse"],
	});
	vnode.value = reusedNode;
}

watch([fields.proxyId, proxyDefinition], render, { immediate: true });
</script>
