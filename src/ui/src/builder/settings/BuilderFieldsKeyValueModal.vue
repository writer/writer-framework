<template>
	<WdsModal
		title="Category key values"
		display-close-button
		:actions="actions"
		@close="$emit('close')"
	>
		<template #titleActions>
			<WdsTabs
				v-model="mode"
				class="BuilderFieldsKeyValueModal__tabs"
				:tabs="tabs"
			/>
		</template>

		<template #default>
			<BuilderEmbeddedCodeEditor
				v-if="mode === 'freehand'"
				v-model="freehandValue"
				class="BuilderFieldsKeyValueModal__freehand"
				variant="minimal"
				language="json"
			/>

			<div
				v-if="mode === 'assisted'"
				class="BuilderFieldsKeyValueModal__assistedEntries"
			>
				<div
					v-if="mode === 'assisted'"
					class="BuilderFieldsKeyValueModal__assistedEntries__form"
				>
					<p
						class="BuilderFieldsKeyValueModal__assistedEntries__form__labelKey"
					>
						Key
					</p>
					<p
						class="BuilderFieldsKeyValueModal__assistedEntries__form__labelValue"
					>
						Value
					</p>
					<template v-for="(entry, id) of assistedEntries" :key="id">
						<WdsFieldWrapper :error="getAssistedEntryError(id)">
							<BuilderTemplateInput
								placeholder="Type a key..."
								:value="entry.key"
								:error="getAssistedEntryError(id)"
								@update:value="
									updateAssistedEntryKey(id, $event)
								"
							/>
						</WdsFieldWrapper>
						<WdsFieldWrapper>
							<BuilderTemplateInput
								placeholder="Type a value..."
								:value="entry.value"
								@update:value="
									updateAssistedEntryValue(id, $event)
								"
							/>
						</WdsFieldWrapper>
						<div>
							<WdsButton
								variant="neutral"
								size="smallIcon"
								class="BuilderFieldsKeyValueModal__assistedEntries__form__deleteBtn"
								@click="removeAssistedEntry(id)"
							>
								<WdsIcon name="trash-2" />
							</WdsButton>
						</div>
					</template>
				</div>

				<WdsButton
					variant="special"
					size="small"
					@click="addAssistedEntry"
				>
					<WdsIcon name="plus" />
					Add a pair
				</WdsButton>
			</div>
		</template>
	</WdsModal>
</template>

<script setup lang="ts">
import { computed, defineAsyncComponent } from "vue";
import WdsTabs, { WdsTabOptions } from "@/wds/WdsTabs.vue";
import WdsModal, { ModalAction } from "@/wds/WdsModal.vue";
import BuilderAsyncLoader from "../BuilderAsyncLoader.vue";
import WdsButton from "@/wds/WdsButton.vue";
import WdsIcon from "@/wds/WdsIcon.vue";
import WdsFieldWrapper from "@/wds/WdsFieldWrapper.vue";
import { Mode, useKeyValueEditor } from "./composables/useKeyValueEditor";
import BuilderTemplateInput from "./BuilderTemplateInput.vue";

const BuilderEmbeddedCodeEditor = defineAsyncComponent({
	loader: () => import("../BuilderEmbeddedCodeEditor.vue"),
	loadingComponent: BuilderAsyncLoader,
});

const props = defineProps({
	data: {
		type: String,
		required: true,
	},
});

const {
	mode,
	assistedEntries,
	freehandValue,
	isValid,
	currentValue,
	addAssistedEntry,
	updateAssistedEntryValue,
	updateAssistedEntryKey,
	removeAssistedEntry,
	getAssistedEntryError,
} = useKeyValueEditor(props.data);

const emits = defineEmits({
	submit: (data: string) => typeof data === "string",
	close: () => true,
});

const actions = computed<ModalAction[]>(() => [
	{
		desc: "Save",
		fn: () => emits("submit", currentValue.value),
		disabled: props.data === currentValue.value || !isValid.value,
	},
]);

const tabs: WdsTabOptions<Mode>[] = [
	{ label: "List", value: "assisted" },
	{ label: "JSON", value: "freehand" },
];
</script>

<style scoped>
.BuilderFieldsKeyValueModal__freehand {
	border: 1px solid var(--separatorColor);
	border-radius: 8px;
	overflow: hidden;
}

.BuilderFieldsKeyValueModal__assistedEntries__form {
	display: grid;
	grid-template-columns: 1fr 1fr auto;
	align-items: flex-start;
	gap: 10px;
	margin-bottom: 22px;
}

.BuilderFieldsKeyValueModal__assistedEntries__form__deleteBtn {
	margin-top: 4px;
}
.BuilderFieldsKeyValueModal__assistedEntries__form__labelKey {
	grid-column-start: 1;
}
.BuilderFieldsKeyValueModal__assistedEntries__form__labelValue {
	grid-column-start: 2;
	grid-column-end: -1;
}
</style>
