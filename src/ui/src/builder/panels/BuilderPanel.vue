<template>
	<div class="BuilderPanel" :class="{ collapsed }">
		<div class="collapser">
			<WdsButton
				variant="neutral"
				size="smallIcon"
				data-automation-action="toggle-panel"
				:data-automation-key="panelId"
				:data-writer-tooltip="`Toggle ${name} (${getModifierKeyName()}${keyboardShortcutKey})`"
				@click="togglePanel(panelId)"
			>
				<i class="material-symbols-outlined">{{
					collapsed ? "expand_less" : "expand_more"
				}}</i>
			</WdsButton>
		</div>
		<div class="title">{{ name }}</div>
		<div class="titleCompanion">
			<slot name="titleCompanion"></slot>
		</div>
		<template v-if="!collapsed">
			<Teleport :to="contentsTeleportEl">
				<div :style="{ order }" :data-order="order" class="contents">
					<div class="actions">
						<div class="actionsCompanion">
							<slot name="actionsCompanion"></slot>
						</div>
						<WdsButton
							v-for="(action, actionKey) in actions"
							:key="actionKey"
							:data-writer-tooltip="
								action.name +
								getKeyboardShortcutDescription(
									action.keyboardShortcut,
								)
							"
							data-writer-tooltip-placement="left"
							variant="neutral"
							size="smallIcon"
							:disabled="action.isDisabled"
							@click="action.callback"
							><i class="material-symbols-outlined">{{
								action.icon
							}}</i></WdsButton
						>
					</div>
					<div class="mainContents">
						<slot></slot>
					</div>
				</div>
			</Teleport>
		</template>
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
import { computed, inject, onMounted, onUnmounted } from "vue";

const wfbm = inject(injectionKeys.builderManager);

const panelIds: ("code" | "log")[] = ["code", "log"];

const props = defineProps<{
	panelId: (typeof panelIds)[number];
	name: string;
	actions: BuilderPanelAction[];
	contentsTeleportEl: HTMLElement;
	scrollable: boolean;
	keyboardShortcutKey: string;
}>();

const collapsed = computed(() => !wfbm.openPanels.value.has(props.panelId));
const order = computed(() => panelIds.indexOf(props.panelId));

function togglePanel(panelId: typeof props.panelId) {
	if (wfbm.openPanels.value.has(panelId)) {
		wfbm.openPanels.value.delete(panelId);
		return;
	}
	wfbm.openPanels.value.add(panelId);
}

function handleKeydown(ev: KeyboardEvent) {
	const isMod = isModifierKeyActive(ev);

	if (isMod && ev.key == props.keyboardShortcutKey.toLowerCase()) {
		ev.preventDefault();
		togglePanel(props.panelId);
		return;
	}

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

onMounted(async () => {
	document.addEventListener("keydown", handleKeydown);
});

onUnmounted(() => {
	document.removeEventListener("keydown", handleKeydown);
});
</script>

<style scoped>
.BuilderPanel {
	display: flex;
	gap: 8px;
	align-items: center;
	background: var(--builderBackgroundColor);
}

.title {
	font-size: 14px;
	font-style: normal;
	font-weight: 600;
	line-height: 140%;
}

.titleCompanion {
	margin-left: 8px;
}

.contents {
	display: grid;
	height: 100%;
	grid-template-rows: 36px 1fr;
	grid-template-columns: 1fr;
	overflow: hidden;
}

.actions {
	display: flex;
	justify-content: right;
	align-items: center;
	padding: 0 8px 0 8px;
	gap: 8px;
	border-bottom: 1px solid var(--builderSeparatorColor);
}

.mainContents {
	overflow-x: hidden;
	overflow-y: auto;
}
</style>
