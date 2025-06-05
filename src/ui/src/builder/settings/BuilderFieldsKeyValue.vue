<template>
	<div
		class="BuilderFieldsKeyValue"
		tabindex="-1"
		:data-automation-key="props.fieldKey"
	>
		<div class="BuilderFieldsKeyValue__toolbar">
			<WdsButton
				variant="neutral"
				size="smallIcon"
				data-automation-key="openAssistedMode"
				@click="modalMode = 'assisted'"
			>
				<i class="material-symbols-outlined">edit</i>
			</WdsButton>
		</div>
		<BuilderFieldsKeyValueModal
			v-if="modalMode"
			:data="field"
			:initial-mode="modalMode"
			@submit="onModalSubmit"
			@close="modalMode = undefined"
		/>

		<div
			v-if="Object.keys(evaluatedValue).length === 0"
			class="BuilderFieldsKeyValue__listEmpty"
		>
			<p>There are no key value categories defined</p>
			<WdsButton
				variant="special"
				size="small"
				@click="modalMode = 'assisted'"
			>
				<i class="material-symbols-outlined">keyboard_backspace</i>
				Edit
			</WdsButton>
		</div>
		<ul v-else class="BuilderFieldsKeyValue__list">
			<li
				v-for="(value, key) of evaluatedValue"
				:key
				class="BuilderFieldsKeyValue__list__item"
			>
				<p
					class="BuilderFieldsKeyValue__list__item__key"
					:data-writer-tooltip="key"
					data-writer-tooltip-strategy="overflow"
				>
					{{ key }}
				</p>
				<p
					class="BuilderFieldsKeyValue__list__item__value"
					:data-writer-tooltip="value"
					data-writer-tooltip-strategy="overflow"
				>
					{{ value || "\<empty value\>" }}
				</p>
			</li>
		</ul>
	</div>
</template>

<script lang="ts">
export type JSONValue = Record<string, string | number | null>;
</script>

<script setup lang="ts">
import { PropType, computed, inject, ref, toRef } from "vue";
import injectionKeys from "@/injectionKeys";
import { useEvaluator } from "@/renderer/useEvaluator";
import type { InstancePath } from "@/writerTypes";
import { useComponentActions } from "../useComponentActions";
import WdsButton from "@/wds/WdsButton.vue";
import BuilderFieldsKeyValueModal from "./BuilderFieldsKeyValueModal.vue";
import type { Mode } from "./composables/useKeyValueEditor";

const props = defineProps({
	componentId: { type: String, required: true },
	fieldKey: { type: String, required: true },
	instancePath: { type: Array as PropType<InstancePath>, required: true },
	error: { type: String, required: false, default: undefined },
});

const wf = inject(injectionKeys.core);
const ssbm = inject(injectionKeys.builderManager);
const secretsManager = inject(injectionKeys.secretsManager);

const { setContentValue } = useComponentActions(wf, ssbm);
const { getEvaluatedFields } = useEvaluator(wf, secretsManager);

const componentId = toRef(props, "componentId");
const fieldKey = toRef(props, "fieldKey");

const modalMode = ref<Mode | undefined>();

const evaluatedValue = computed<JSONValue>(
	() => getEvaluatedFields(props.instancePath)[fieldKey.value].value,
);

const component = computed(() => wf.getComponentById(componentId.value));

const field = computed(() => {
	const value = component.value.content?.[fieldKey.value];
	if (value === undefined) return evaluatedValue.value;

	try {
		return JSON.parse(value);
	} catch {
		return {};
	}
});

function onModalSubmit(data: JSONValue) {
	modalMode.value = undefined;
	setContentValue(
		component.value.id,
		fieldKey.value,
		JSON.stringify(data, null, 2),
	);
}
</script>

<style scoped>
.BuilderFieldsKeyValue {
	position: relative;
}
.BuilderFieldsKeyValue__toolbar {
	display: flex;
	gap: 4px;
	justify-content: flex-end;
	position: absolute;
	top: -32px;
	right: 0px;
}

.BuilderFieldsKeyValue__listEmpty,
.BuilderFieldsKeyValue__list {
	border: 1px solid var(--separatorColor);
	border-radius: 8px;
	list-style: none;
}

.BuilderFieldsKeyValue__list__item {
	padding: 12px;
}

.BuilderFieldsKeyValue__list__item:not(:last-child) {
	border-bottom: 1px solid var(--separatorColor);
}

.BuilderFieldsKeyValue__list__item__key,
.BuilderFieldsKeyValue__list__item__value {
	font-size: 12px;
	text-overflow: ellipsis;
	white-space: nowrap;
	overflow: hidden;
}

.BuilderFieldsKeyValue__list__item__key {
	font-size: 12px;
	color: var(--wdsColorGray4);
}

.BuilderFieldsKeyValue__listEmpty {
	height: 150px;
	padding: 12px;
	gap: 18px;
	display: flex;
	flex-direction: column;
	align-items: center;
	justify-content: center;
}
.BuilderFieldsKeyValue__listEmpty p {
	text-align: center;
	color: var(--wdsColorGray4);
	text-wrap: pretty;
}
</style>
