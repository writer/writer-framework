<template>
	<div
		class="BuilderPanel"
		:class="{ collapsed, allPanelsCollapsed }"
		@keydown="handleKeydown"
	>
		<div class="header">
			<div class="collapser">
				<WdsButton
					variant="neutral"
					size="icon"
					@click="togglePanel(panelId)"
				>
					<i class="material-symbols-outlined">
						{{ collapserIcon }}
					</i>
				</WdsButton>
			</div>
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
		<div v-if="!collapsed" class="content"><slot></slot></div>
	</div>
</template>

<script lang="ts">
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
</script>

<script setup lang="ts">
import { getModifierKeyName, isModifierKeyActive } from "@/core/detectPlatform";
import injectionKeys from "@/injectionKeys";
import WdsButton from "@/wds/WdsButton.vue";
import { computed, inject } from "vue";

const wfbm = inject(injectionKeys.builderManager);

const panelIds: ("code" | "log")[] = ["code", "log"];

const props = defineProps<{
	panelId: (typeof panelIds)[number];
	name: string;
	actions: BuilderPanelAction[];
}>();

const collapsed = computed(() => !wfbm.openPanels.value.has(props.panelId));
const allPanelsCollapsed = computed(() => wfbm.openPanels.value.size == 0);

const collapserIcon = computed(() => {
	function getIcons() {
		const openPanelCount = wfbm.openPanels.value.size;
		if (openPanelCount == 0) {
			return ["expand_less", "expand_less"];
		}
		if (openPanelCount == panelIds.length) {
			return ["chevron_left", "chevron_right"];
		}
		if (wfbm.openPanels.value.has(panelIds[0])) {
			return ["expand_more", "chevron_left"];
		}
		return ["chevron_right", "expand_more"];
	}

	return getIcons()[panelIds.indexOf(props.panelId)];
});

function togglePanel(panelId: typeof props.panelId) {
	if (wfbm.openPanels.value.has(panelId)) {
		wfbm.openPanels.value.delete(panelId);
		return;
	}
	wfbm.openPanels.value.add(panelId);
}

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
	flex: 1 1 50%;
	border-top: 1px solid var(--builderIntenseSeparatorColor);
	display: grid;
	background: var(--builderBackgroundColor);
	grid-template-rows: 48px 1fr;
	grid-template-columns: 1fr;
}

.BuilderPanel.allPanelsCollapsed {
	grid-template-rows: 1fr;
}

.BuilderPanel.collapsed {
	flex: 0 1 96px;
}

.BuilderPanel.allPanelsCollapsed:last-child {
	flex: 1 0 96px;
}

.BuilderPanel:not(:first-child) {
	border-left: 1px solid var(--builderSeparatorColor);
}

.header {
	grid-column: 1 / 2;
	grid-row: 1 / 2;
	display: flex;
	align-items: center;
	padding: 8px;
	gap: 8px;
	flex-direction: row;
}

.BuilderPanel:not(.collapsed) .header {
	border-bottom: 1px solid var(--builderSeparatorColor);
}

.BuilderPanel.collapsed:not(.allPanelsCollapsed) .header {
	flex-direction: column;
	grid-template-rows: 1fr;
	height: 100%;
}

.header .title {
	font-size: 14px;
	font-style: normal;
	font-weight: 600;
	line-height: 140%;
}

.header .gap {
	flex: 1 0 auto;
}

.header .actions {
	display: flex;
	font-size: 16px;
}

.content {
	grid-column: 1 / 2;
	grid-row: 2 / 3;
	overflow: auto;
	width: 100%;
}
</style>
