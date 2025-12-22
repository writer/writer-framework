<template>
	<div class="BlueprintsNavigationStack" data-writer-unselectable>
		<div
			v-if="displayedBlueprintId || displayedBlueprintKey"
			class="BlueprintsNavigationStack_container"
		>
			<WdsButton
				size="smallIcon"
				variant="tertiary"
				class="BlueprintsNavigationStack_button"
				:disabled="!wf.canGoBackInPageStack()"
				data-writer-tooltip-placement="bottom"
				data-writer-unselectable
				:data-writer-tooltip="previousBlueprintTooltip"
				@click="handlePreviousBlueprint"
			>
				<WdsIcon name="chevron-left" />
			</WdsButton>
			<WdsButton
				size="smallIcon"
				variant="tertiary"
				class="BlueprintsNavigationStack_button"
				:disabled="!wf.canGoForwardInPageStack()"
				data-writer-tooltip-placement="bottom"
				data-writer-unselectable
				:data-writer-tooltip="nextBlueprintTooltip"
				@click="handleNextBlueprint"
			>
				<WdsIcon name="chevron-right" />
			</WdsButton>

			<span class="BlueprintsNavigationStack_title_prefix">
				Blueprint:
			</span>
			<div>
				{{
					displayedBlueprintKey
						? displayedBlueprintKey
						: displayedBlueprintId
				}}
			</div>
			<div v-if="selectedItemKey">> {{ selectedItemKey }}</div>
		</div>
	</div>
</template>

<script setup lang="ts">
import { useComponentInformation } from "@/composables/useComponentInformation";
import injectionKeys from "@/injectionKeys";
import { computed, inject, onMounted, onUnmounted } from "vue";
import WdsButton from "@/wds/WdsButton.vue";
import WdsIcon from "@/wds/WdsIcon.vue";

const wf = inject(injectionKeys.core);
const wfbm = inject(injectionKeys.builderManager);

const displayedBlueprintId = computed(() => {
	const activePageId = wf.activePageId.value;
	const activePageExists = Boolean(wf.getComponentById(activePageId));
	if (activePageExists && wf.isChildOf("blueprints_root", activePageId))
		return activePageId;

	const pageComponents = wf.getComponents("blueprints_root", {
		includeBMC: true,
		includeCMC: false,
		sortedByPosition: true,
	});
	if (pageComponents.length == 0) return null;

	return pageComponents[0].id;
});

const displayedBlueprintKey = computed(() => {
	const displayedBlueprint = wf.getComponentById(displayedBlueprintId.value);
	return displayedBlueprint?.content?.key;
});

const selectedItemKey = computed(() => {
	if (wfbm.selection.value.length > 1) {
		return null;
	}

	const { component, definition: def } = useComponentInformation(
		wf,
		wfbm.firstSelectedId,
	);
	if (!component.value || component.value.type === "blueprints_blueprint") {
		return null;
	}

	return component.value?.content?.alias || def.value?.name || "Unknown";
});

// Detect if the user is on macOS
const isMac = computed(() => {
	// Try modern User-Agent Client Hints API first
	const userAgentData = (navigator as any).userAgentData;
	if (userAgentData?.platform) {
		return userAgentData.platform.toLowerCase().includes("mac");
	}

	// Fall back to checking userAgent string
	return /Mac|iPhone|iPad|iPod/.test(navigator.userAgent);
});

const previousBlueprintTooltip = computed(() => {
	const shortcut = isMac.value ? "⌃-" : "Ctrl+-";
	if (!wf.canGoBackInPageStack()) return `(${shortcut})`;

	const previousPage = wf.getPreviousPageInPageStack();
	if (!previousPage?.key) return `Go to previous blueprint (${shortcut})`;
	return `${previousPage.key} (${shortcut})`;
});

const nextBlueprintTooltip = computed(() => {
	const shortcut = isMac.value ? "⌃⇧-" : "Ctrl+Shift+-";
	if (!wf.canGoForwardInPageStack()) return `(${shortcut})`;

	const nextPage = wf.getNextPageInPageStack();
	if (!nextPage?.key) return `Go to next blueprint (${shortcut})`;
	return `${nextPage.key} (${shortcut})`;
});

function handleNextBlueprint(ev: MouseEvent | KeyboardEvent) {
	if (wf.canGoForwardInPageStack()) {
		ev.preventDefault();
		ev.stopPropagation();
		wfbm.setSelection(null);
		wf.navigateInPageStack(null, "forward");
	}
}

function handlePreviousBlueprint(ev: MouseEvent | KeyboardEvent) {
	if (wf.canGoBackInPageStack()) {
		ev.preventDefault();
		ev.stopPropagation();
		wfbm.setSelection(null);
		wf.navigateInPageStack(null, "backward");
	}
}

function handleKeyboardShortcut(event: KeyboardEvent) {
	// Use Ctrl key on both Mac and Windows/Linux
	const modifierKey = event.ctrlKey;

	// Check for Ctrl+- - Go back
	if (modifierKey && !event.shiftKey && event.key === "-") {
		handlePreviousBlueprint(event);
		return;
	}

	// Check for Ctrl+Shift+- - Go forward
	// Note: Shift+- produces "_" on most keyboards
	if (
		modifierKey &&
		event.shiftKey &&
		(event.key === "_" || event.key === "-")
	) {
		handleNextBlueprint(event);
		return;
	}
}

onMounted(() => {
	window.addEventListener("keydown", handleKeyboardShortcut);
});

onUnmounted(() => {
	window.removeEventListener("keydown", handleKeyboardShortcut);
});
</script>

<style scoped>
@import "@/renderer/sharedStyles.css";

.BlueprintsNavigationStack {
	position: absolute;
	top: 24px;
	left: 24px;
	z-index: 10;
}

.BlueprintsNavigationStack_container {
	font-family: Poppins, "Helvetica Neue", "Lucida Grande", sans-serif;
	font-size: 10px;
	font-weight: 500;
	line-height: 10px; /* 100% */
	letter-spacing: 0.5px;
	text-transform: none;
	z-index: 1;
	pointer-events: none;
	user-select: none;
	background: var(--builderSubtleSeparatorColor);
	padding: 8px;
	border-radius: 8px;
	border: 1px solid var(--builderSeparatorColor);
	display: flex;
	align-items: center;
	gap: 4px;
}

.BlueprintsNavigationStack_title_prefix {
	text-transform: none;
	color: var(--builderSecondaryTextColor);
}

.BlueprintsNavigationStack_button {
	width: 20px;
	height: 20px;
	background: var(--builderSeparatorColor);
	cursor: pointer;
	pointer-events: auto;
}

.BlueprintsNavigationStack_button:focus {
	color: inherit;
}

.BlueprintsNavigationStack_button:disabled {
	opacity: 0.5;
	cursor: default;
}
.BlueprintsNavigationStack_button:deep(svg) {
	width: 12px;
	height: 12px;
}
</style>
