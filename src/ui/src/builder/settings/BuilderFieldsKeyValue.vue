<template>
	<div
		ref="rootEl"
		class="BuilderFieldsOptions"
		tabindex="-1"
		:data-automation-key="props.fieldKey"
	>
		<WdsButton variant="special" size="small" @click="isModalOpen = true">
			<i class="material-symbols-outlined">keyboard_backspace</i>
			Edit
		</WdsButton>
		<BuilderFieldsKeyValueModal
			v-if="isModalOpen"
			:data="evaluatedValue"
			@submit="onModalSubmit"
			@close="isModalOpen = false"
		/>

		<p>{{ evaluatedValue }}</p>
	</div>
</template>

<script lang="ts">
export type JSONValue = Record<string, string | number | null>;
</script>

<script setup lang="ts">
import { PropType, computed, inject, ref, toRefs, useTemplateRef } from "vue";
import injectionKeys from "@/injectionKeys";
import { useEvaluator } from "@/renderer/useEvaluator";
import type { InstancePath } from "@/writerTypes";
import { useComponentActions } from "../useComponentActions";
import WdsButton from "@/wds/WdsButton.vue";
import BuilderFieldsKeyValueModal from "./BuilderFieldsKeyValueModal.vue";

const wf = inject(injectionKeys.core);
const ssbm = inject(injectionKeys.builderManager);
const { setContentValue } = useComponentActions(wf, ssbm);

const isModalOpen = ref(false);

const props = defineProps({
	componentId: { type: String, required: true },
	fieldKey: { type: String, required: true },
	instancePath: { type: Array as PropType<InstancePath>, required: true },
	error: { type: String, required: false, default: undefined },
});

function onModalSubmit(data: JSONValue) {
	isModalOpen.value = false;
	setContentValue(
		component.value.id,
		fieldKey.value,
		JSON.stringify(data, null, 2),
	);
}

const { componentId, fieldKey } = toRefs(props);
const component = computed(() => wf.getComponentById(componentId.value));

const rootEl = useTemplateRef("rootEl");

const { getEvaluatedFields } = useEvaluator(wf);

const evaluatedValue = computed<JSONValue>(
	() => getEvaluatedFields(props.instancePath)[fieldKey.value].value,
);
</script>

<style scoped>
@import "../sharedStyles.css";

.BuilderFieldsOptions__tabs {
	margin-bottom: 8px;
}

.staticList {
	padding: 8.5px 12px 8.5px 12px;
	border: 1px solid var(--builderSeparatorColor);
	border-radius: 8px;
}
.staticList--invalid {
	border-color: var(--wdsColorOrange5);
}

.staticList:empty::before {
	content: "No entries yet.";
}

.staticList .entry {
	display: flex;
	align-items: center;
	gap: 8px;
	width: 100%;
	max-width: 100%;
}

.staticList .entry div {
	overflow: hidden;
	padding-top: 4px;
	padding-bottom: 4px;
	flex: 1 1 auto;
}

.staticList .entry button {
	flex: 0 0 auto;
}

.formAdd {
	margin-top: 8px;
}

.BuilderTemplateInput {
	margin-bottom: 8px;
}
</style>
