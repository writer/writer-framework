<template>
	<div class="BuilderPanel" :class="{ collapsed }">
		<div class="BuilderPanel__collapser">
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
		<div class="BuilderPanel__title">{{ name }}</div>
		<div class="BuilderPanel__titleCompanion">
			<slot name="titleCompanion"></slot>
		</div>
		<template v-if="!collapsed">
			<Teleport :to="contentsTeleportEl">
				<div
					:style="{ order }"
					:data-order="order"
					class="BuilderPanel__contents"
					:class="{
						'BuilderPanel__contents--leftPanel': enableLeftPanel,
						'BuilderPanel__contents--dropingFile':
							showDropingFilesZone,
					}"
					@drop="handleDrop"
					@dragover="handleDragEvent($event, true)"
					@dragleave="handleDragEvent($event, false)"
				>
					<BuilderDropFileZone v-if="showDropingFilesZone" />
					<template v-else>
						<div
							v-if="enableLeftPanel"
							class="BuilderPanel__contents__leftPanel"
						>
							<slot name="leftPanel" />
						</div>
						<div class="BuilderPanel__actions">
							<div class="BuilderPanel__actionsCompanion">
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
						<div class="BuilderPanel__mainContents">
							<slot></slot>
						</div>
					</template>
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
import { computed, inject, onMounted, onUnmounted, ref } from "vue";
import BuilderDropFileZone from "../BuilderDropFileZone.vue";

const wfbm = inject(injectionKeys.builderManager);

const panelIds: ("code" | "log")[] = ["code", "log"];

const props = defineProps<{
	panelId: (typeof panelIds)[number];
	name: string;
	actions: BuilderPanelAction[];
	contentsTeleportEl: HTMLElement;
	scrollable: boolean;
	keyboardShortcutKey: string;
	enableLeftPanel?: boolean;
	enableDropFile?: boolean;
}>();

const emits = defineEmits({
	openned: (open: boolean) => typeof open === "boolean",
	fileDrop: (files: File[]) => Array.isArray(files) && files.length > 0,
});

const showDropingFilesZone = computed(
	() => props.enableDropFile && isDropingFiles.value,
);

const isDropingFiles = ref(false);

function handleDragEvent(event: DragEvent, hover: boolean) {
	if (!props.enableDropFile) return;

	event.preventDefault();
	isDropingFiles.value = hover;
}

function handleDrop(event: DragEvent) {
	isDropingFiles.value = false;

	if (!props.enableDropFile) return;
	event.preventDefault();

	const files: File[] = [];

	if (event.dataTransfer.items) {
		for (const item of event.dataTransfer.items) {
			if (item.kind !== "file") continue;
			const file = item.getAsFile();
			if (file) files.push(file);
		}
	} else {
		for (const file of event.dataTransfer.files) {
			files.push(file);
		}
	}

	if (files.length > 0) emits("fileDrop", files);
}

const collapsed = computed(() => !wfbm.openPanels.value.has(props.panelId));
const order = computed(() => panelIds.indexOf(props.panelId));

function togglePanel(panelId: typeof props.panelId) {
	if (wfbm.openPanels.value.has(panelId)) {
		wfbm.openPanels.value.delete(panelId);
		emits("openned", false);
		return;
	}
	wfbm.openPanels.value.add(panelId);
	emits("openned", true);
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

.BuilderPanel__title {
	font-size: 14px;
	font-style: normal;
	font-weight: 600;
	line-height: 140%;
}

.BuilderPanel__titleCompanion {
	margin-left: 8px;
}

.BuilderPanel__contents {
	display: grid;
	height: 100%;
	grid-template-rows: 56px 1fr;
	grid-template-columns: 1fr;
	overflow: hidden;
}

.BuilderPanel__contents--leftPanel {
	grid-template-columns: auto 1fr;
}
.BuilderPanel__contents--dropingFile {
	grid-template-columns: 1fr;
	grid-template-rows: 1fr;
}

.BuilderPanel__contents__leftPanel {
	width: 200px;
	height: 100%;
	grid-row: 1 / 3;
	border-right: 1px solid var(--builderSeparatorColor);
}

.BuilderPanel__actions,
.BuilderPanel__actionsCompanion {
	width: 100%;
}

.BuilderPanel__actions {
	display: flex;
	justify-content: right;
	align-items: center;
	padding: 0 8px 0 8px;
	gap: 8px;
	border-bottom: 1px solid var(--builderSeparatorColor);
}

.BuilderPanel__mainContents {
	overflow-x: hidden;
	overflow-y: auto;
}
</style>
