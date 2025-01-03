<template>
	<div class="selector-container">
		<div class="form">
			<label class="title__label">Action</label>
			<div class="input">
				<input
					class="selector-input"
					:value="actionName"
					type="text"
					placeholder="..."
					readonly
					@input="handleInput"
					@focus="showSuggestions = true"
				/>
			</div>
		</div>

		<ul v-if="showSuggestions" class="suggestions-list">
			<li
				v-for="option of options"
				:key="option.type"
				class="suggestion-item"
				@click="selectOption(option.type)"
			>
				{{ option.name }}
			</li>
		</ul>
	</div>
</template>

<script setup lang="ts">
import { computed, inject, ref } from "vue";
import injectionKeys from "@/injectionKeys";

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
			type: availableActions.value[_action].type,
			name: availableActions.value[_action].name,
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

const showSuggestions = ref(false);

function handleInput() {
	showSuggestions.value = true;
}

function selectOption(selected: string) {
	const hasAction = wf.hasComponentDefinition(selected);
	if (hasAction) {
		component.value.type = selected;
		showSuggestions.value = false;
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
