<template>
	<div class="BuilderSwitcher">
		<div
			data-automation-action="set-mode-ui"
			:class="{ active: activeId == 'ui' }"
			@click="selectOption('ui')"
		>
			<i class="icon material-symbols-outlined"> brush </i>
			UI
		</div>
		<div
			data-automation-action="set-mode-workflows"
			:class="{ active: activeId == 'workflows' }"
			@click="selectOption('workflows')"
		>
			<i class="icon material-symbols-outlined"> linked_services </i>
			Workflows
		</div>
		<div
			:class="{ active: activeId == 'preview' }"
			data-automation-action="set-mode-preview"
			@click="selectOption('preview')"
		>
			<i class="icon material-symbols-outlined"> preview </i>
			Preview
		</div>
	</div>
</template>

<script setup lang="ts">
import { computed, inject, Ref, ref } from "vue";
import injectionKeys from "@/injectionKeys";

const ssbm = inject(injectionKeys.builderManager);

let selectedId: Ref<string> = ref(null);

const selectOption = (optionId: "ui" | "preview" | "workflows") => {
	const preMode = ssbm.getMode();
	if (preMode == optionId) return;
	selectedId.value = optionId;
	ssbm.setMode(optionId);
	if (
		optionId == "preview" ||
		preMode == "workflows" ||
		optionId == "workflows"
	) {
		ssbm.setSelection(null);
	}
};

const activeId = computed(() => ssbm.getMode());
</script>

<style scoped>
@import "./sharedStyles.css";

.BuilderSwitcher {
	background: var(--builderHeaderBackgroundHoleColor);
	color: white;
	font-size: 0.75rem;
	display: flex;
	gap: 0px;
	padding: 4px;
	border-radius: 8px;
	overflow: hidden;
}

.BuilderSwitcher div {
	padding: 4px 12px 4px 12px;
	cursor: pointer;
	display: flex;
	align-items: center;
}

.BuilderSwitcher .icon {
	margin-right: 8px;
}

.BuilderSwitcher div.active {
	background: var(--builderHeaderBackgroundColor);
	border-radius: 4px;
}
</style>
