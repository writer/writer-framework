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
				@click="isModalOpen = true"
			>
				<WdsIcon name="pencil" />
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
				<WdsIcon name="pencil" />
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
import { useComponentFieldViewModel } from "../useComponentFieldViewModel";
import WdsButton from "@/wds/WdsButton.vue";
import WdsIcon from "@/wds/WdsIcon.vue";
import BuilderFieldsKeyValueModal from "./BuilderFieldsKeyValueModal.vue";

const props = defineProps({
	componentId: { type: String, required: true },
	fieldKey: { type: String, required: true },
	instancePath: { type: Array as PropType<InstancePath>, required: true },
	error: { type: String, required: false, default: undefined },
});

const fieldViewModel = useComponentFieldViewModel({
	componentId: toRef(props, "componentId"),
	fieldKey: toRef(props, "fieldKey"),
});

const wf = inject(injectionKeys.core);
const secretsManager = inject(injectionKeys.secretsManager);

const { getEvaluatedFields } = useEvaluator(wf, secretsManager);

const isModalOpen = ref(false);

const evaluatedValue = computed<JSONValue>(
	() => getEvaluatedFields(props.instancePath)?.[props.fieldKey].value ?? {},
);

const field = computed(
	() => fieldViewModel.value || JSON.stringify(evaluatedValue.value),
);

function onModalSubmit(data: string) {
	isModalOpen.value = false;
	fieldViewModel.value = data;
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
