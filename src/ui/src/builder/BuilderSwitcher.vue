<template>
	<div class="BuilderSwitcher">
		<button
			data-automation-action="set-mode-ui"
			:class="{ active: activeId == 'ui' }"
			type="button"
			@click="selectOption('ui')"
		>
			<i class="icon material-symbols-outlined"> brush </i>
			UI
		</button>
		<button
			data-automation-action="set-mode-blueprints"
			:class="{ active: activeId == 'blueprints' }"
			type="button"
			@click="selectOption('blueprints')"
		>
			<i class="icon material-symbols-outlined">linked_services</i>
			Blueprints
		</button>
		<button
			:class="{ active: activeId == 'preview' }"
			data-automation-action="set-mode-preview"
			type="button"
			@click="selectOption('preview')"
		>
			<i class="icon material-symbols-outlined"> preview </i>
			Preview
		</button>
	</div>
</template>

<script setup lang="ts">
import { computed, inject, Ref, ref } from "vue";
import injectionKeys from "@/injectionKeys";

const ssbm = inject(injectionKeys.builderManager);

let selectedId: Ref<string> = ref(null);

const selectOption = (optionId: "ui" | "preview" | "blueprints") => {
	const preMode = ssbm.getMode();
	if (preMode == optionId) return;
	selectedId.value = optionId;
	ssbm.setMode(optionId);
	if (
		optionId == "preview" ||
		preMode == "blueprints" ||
		optionId == "blueprints"
	) {
		ssbm.setSelection(null);
	}
};

const activeId = computed(() => ssbm.getMode());
</script>

<style scoped>
@import "./sharedStyles.css";

.BuilderSwitcher {
	display: flex;
	gap: 0px;
	overflow: hidden;
}

.BuilderSwitcher button {
	background-color: transparent;
	color: white;
	border: none;

	font-size: 14px;

	padding: 4px 12px 4px 12px;
	cursor: pointer;
	display: flex;
	align-items: center;
	gap: 4px;
	height: 32px;
	border-radius: 4px;
}

.BuilderSwitcher .icon {
	margin-right: 8px;
}

.BuilderSwitcher .active {
	background: var(--builderHeaderBackgroundHoleColor);
}
</style>
