<template>
	<div class="BuilderPanel" @keydown="handleKeydown">
		<div class="header">
			<div class="title">{{ name }}</div>
			<div class="titleCompanion">
				<slot name="titleCompanion"></slot>
			</div>
			<div class="gap"></div>
			<div class="actionsCompanion">
				<slot name="actionsCompanion"></slot>
			</div>
			<WdsButton
				v-for="(action, actionKey) in actions"
				:key="actionKey"
				:data-writer-tooltip="
					action.name +
					getKeyboardShortcutDescription(action.keyboardShortcut)
				"
				data-writer-tooltip-placement="left"
				variant="neutral"
				size="unpadded"
				:disabled="action.isDisabled"
				@click="action.callback"
				><i class="material-symbols-outlined">{{
					action.icon
				}}</i></WdsButton
			>
		</div>
		<div class="content"><slot></slot></div>
	</div>
</template>

<script setup lang="ts">
import { getModifierKeyName, isModifierKeyActive } from "@/core/detectPlatform";
import WdsButton from "@/wds/WdsButton.vue";

export type BuilderPanelAction = {
	icon: string;
	name: string;
	callback: () => void;
	isDisabled?: boolean;
	keyboardShortcut?: {
		modifierKey: boolean;
		key: string;
	};
};

const props = defineProps<{
	name: string;
	actions: BuilderPanelAction[];
}>();

function handleKeydown(ev: KeyboardEvent) {
	const isMod = isModifierKeyActive(ev);

	props.actions.forEach((action) => {
		if (!action.keyboardShortcut) return;
		const { key, modifierKey } = action.keyboardShortcut;
		if (key.toLowerCase() != ev.key) return;
		if (!isMod && modifierKey) return;
		ev.preventDefault();
		action.callback();
	});
}

function getKeyboardShortcutDescription(
	shortcut: BuilderPanelAction["keyboardShortcut"],
) {
	if (!shortcut) return "";
	let s = " (";
	if (shortcut.modifierKey) {
		s += getModifierKeyName();
	}
	s += shortcut.key;
	s += ")";
	return s;
}
</script>

<style scoped>
@import "./sharedStyles.css";

.BuilderPanel {
	border-top: 1px solid var(--builderSeparatorColor);
	display: grid;
	background: var(--builderBackgroundColor);
	grid-template-rows: 36px 1fr;
	grid-template-columns: 1fr;
	height: 100%;
}

.BuilderPanel:not(:first-child) {
	border-left: 1px solid var(--builderSeparatorColor);
}

.header {
	grid-column: 1 / 2;
	grid-row: 1 / 2;
	display: flex;
	align-items: center;
	padding: 8px 8px 8px 20px;
	border-bottom: 1px solid var(--builderSeparatorColor);
	gap: 12px;
}

.header .title {
	font-size: 14px;
	font-style: normal;
	font-weight: 600;
	line-height: 140%;
}

.header .titleCompanion {
}

.header .gap {
	flex: 1 0 auto;
}

.header .actionsCompanion {
}

.header .actions {
	display: flex;
	font-size: 16px;
}

.content {
	grid-column: 1 / 2;
	grid-row: 2 / 3;
	overflow: auto;
}
</style>
