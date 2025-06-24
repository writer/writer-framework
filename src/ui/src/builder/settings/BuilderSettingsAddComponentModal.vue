<template>
	<WdsModal
		v-if="isOpen"
		title="Add child component"
		display-close-button
		@close="closeModal"
	>
		<WdsTextInput
			type="text"
			:list="datalistId"
			placeholder="Component..."
			@change="addComponent"
		/>
		<datalist :id="datalistId">
			<option
				v-for="(definition, type) in validChildrenTypes"
				:key="type"
				:value="definition.name"
			>
				{{ definition.name }}
			</option>
		</datalist>
	</WdsModal>
</template>

<script setup lang="ts">
import { computed, inject, useId } from "vue";
import { useComponentActions } from "../useComponentActions";
import { WriterComponentDefinition } from "@/writerTypes";
import injectionKeys from "@/injectionKeys";
import WdsModal from "@/wds/WdsModal.vue";
import { useWriterTracking } from "@/composables/useWriterTracking";
import WdsTextInput from "@/wds/WdsTextInput.vue";

const wf = inject(injectionKeys.core);
const ssbm = inject(injectionKeys.builderManager);

const datalistId = useId();

const tracking = useWriterTracking(wf);

const { createAndInsertComponent } = useComponentActions(wf, ssbm, tracking);

const props = defineProps({
	selectedId: { type: String, required: true },
});

const validChildrenTypes = computed(() => {
	return wf
		.getContainableTypes(props.selectedId)
		.reduce<Record<string, WriterComponentDefinition>>((acc, type) => {
			acc[type] = wf.getComponentDefinition(type);
			return acc;
		}, {});
});

const isOpen = defineModel("isOpen", { type: Boolean, default: false });

function closeModal() {
	isOpen.value = false;
}

function addComponent(event: Event) {
	const definitionName = (event.target as HTMLInputElement).value;
	if (!definitionName) return;

	const matchingType = Object.entries(validChildrenTypes.value).find(
		([_, definition]) => {
			if (definition.name == definitionName) return true;
			return false;
		},
	);
	if (!matchingType) return;
	const type = matchingType[0];
	createAndInsertComponent(type, props.selectedId);
	closeModal();
}
</script>
