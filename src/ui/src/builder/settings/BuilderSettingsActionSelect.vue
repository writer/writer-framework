<template>
	<div class="selector-container">
		<BuilderSelect
			:model-value="actionName"
			:options="options"
			:hide-icons="true"
			@update:model-value="selectOption"
		/>
	</div>
</template>

<script setup lang="ts">
import { computed, defineAsyncComponent, inject } from "vue";
import injectionKeys from "@/injectionKeys";
import BuilderAsyncLoader from "@/builder/BuilderAsyncLoader.vue";

const BuilderSelect = defineAsyncComponent({
	loader: () => import("../BuilderSelect.vue"),
	loadingComponent: BuilderAsyncLoader,
});

const wf = inject(injectionKeys.core);
const ssbm = inject(injectionKeys.builderManager);

const component = computed(() => {
	return wf.getComponentById(ssbm.firstSelectedId.value);
});

const availableActions = computed(() => {
	return wf.getAvailableActions(component.value.type);
});

const options = computed(() => {
	const options = [];
	for (const _action of Object.keys(availableActions.value)) {
		options.push({
			value: availableActions.value[_action].type,
			label: availableActions.value[_action].name,
		});
	}
	return options;
});

const actionName = computed(() => {
	const _actionName = wf.getActionName(component.value.type);
	if (_actionName) {
		return _actionName;
	} else {
		return "";
	}
});

function selectOption(selected: string) {
	const hasAction = wf.hasComponentDefinition(selected);
	if (hasAction) {
		component.value.type = selected;
	}
}
</script>

<style scoped>
@import "../sharedStyles.css";
.form {
	display: flex;
	flex-direction: column;
	gap: 4px;
}

.title__label {
	font-size: 14px;
	font-weight: 500;
	line-height: 20px;
}

.selector-container {
	position: relative;
}

.input {
	width: 100%;
	border: 1px solid #ccc;
	border-radius: 8px;
	padding: 8px;

	display: flex;
	flex-direction: row;
	gap: 4px;
}

.selector-input {
	width: 100%;
	border: none;
	outline: none;
}

.suggestions-list {
	position: absolute;
	left: 0;
	right: 0;
	background: white;
	border: 1px solid #ccc;
	border-top: none;
	border-radius: 0 0 4px 4px;
	max-height: 200px;
	overflow-y: auto;
	z-index: 1000;
	margin: 0 24px;
}

.suggestion-item {
	padding: 8px;
	cursor: pointer;
}

.suggestion-item:hover {
	background-color: #f0f0f0;
}
</style>
