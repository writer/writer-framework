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
				@click="isModalOpen = true"
			>
				<i class="material-symbols-outlined">edit</i>
			</WdsButton>
			<WdsButton
				variant="neutral"
				size="smallIcon"
				@click="isModalOpen = true"
			>
				<i class="material-symbols-outlined">code</i>
			</WdsButton>
		</div>
		<BuilderFieldsKeyValueModal
			v-if="isModalOpen"
			:data="field"
			@submit="onModalSubmit"
			@close="isModalOpen = false"
		/>

		<div
			v-if="Object.keys(evaluatedValue).length === 0"
			class="BuilderFieldsKeyValue__listEmpty"
		>
			<p>There are no key value categories defined</p>
			<WdsButton
				variant="special"
				size="small"
				@click="isModalOpen = true"
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
				<p class="BuilderFieldsKeyValue__list__item__key">{{ key }}</p>
				<p class="BuilderFieldsKeyValue__list__item__value">
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
import { PropType, computed, inject, ref, toRefs } from "vue";
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

const field = computed(() => {
	try {
		return JSON.parse(component.value.content[fieldKey.value] ?? "{}");
	} catch {
		return {};
	}
});

const { getEvaluatedFields } = useEvaluator(wf);

const evaluatedValue = computed<JSONValue>(
	() => getEvaluatedFields(props.instancePath)[fieldKey.value].value,
);
</script>

<style scoped>
.BuilderFieldsKeyValue {
	position: relative;
}
.BuilderFieldsKeyValue__toolbar {
	display: flex;
	gap: 4px;
	justify-content: flex-end;
	/* TODO: temporary trick */
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

.BuilderFieldsKeyValue__list__item__key {
	font-size: 12px;
	color: var(--wdsColorGray4);
}

.BuilderFieldsKeyValue__list__item__value {
	font-size: 12px;
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
