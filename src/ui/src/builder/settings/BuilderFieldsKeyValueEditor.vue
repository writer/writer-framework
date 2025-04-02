<template>
	<div class="BuilderFieldsKeyValueEditor">
		<div class="BuilderFieldsKeyValueEditor__entries">
			<template v-for="(key, value) of model" :key="key">
				<WdsFieldWrapper label="Key">
					<WdsTextInput
						:model-value="String(key)"
						@update:model-value="
							handleUpdateKey(String(key), $event)
						"
					/>
				</WdsFieldWrapper>
				<WdsFieldWrapper label="Value">
					<WdsTextInput
						:model-value="String(value)"
						@update:model-value="
							handleUpdateValue(String(key), $event)
						"
					/>
				</WdsFieldWrapper>
			</template>
		</div>

		<WdsButton
			variant="special"
			size="small"
			:disabled="addPairDisabled"
			@click="addPair"
			><span class="material-symbols-outlined">add</span>Add a
			pair</WdsButton
		>
	</div>
</template>

<script setup lang="ts">
import { computed, PropType } from "vue";
import type { JSONValue } from "./BuilderFieldsKeyValue.vue";
import WdsButton from "@/wds/WdsButton.vue";
import WdsFieldWrapper from "@/wds/WdsFieldWrapper.vue";
import WdsTextInput from "@/wds/WdsTextInput.vue";

const model = defineModel({ type: Object as PropType<JSONValue> });

function addPair() {
	model.value = { ...model.value, "": "" };
}

function handleUpdateKey(prev: string, next: string) {
	const copy = { ...model.value };
	copy[next] = copy[prev];
	delete copy[prev];
	model.value = copy;
}
function handleUpdateValue(key: string, value: string) {
	model.value = {
		...model.value,
		[key]: value,
	};
}

const addPairDisabled = computed(() => model.value[""] !== undefined);
</script>

<style scoped>
.BuilderFieldsKeyValueEditor__entries {
	display: grid;
	grid-template-columns: 1fr 1fr;
	gap: 10px;
	margin-bottom: 22px;
}
</style>
