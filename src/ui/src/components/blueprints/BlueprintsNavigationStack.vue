<template>
	<div class="BlueprintsNavigationStack" data-writer-unselectable>
		<div class="BlueprintsNavigationStack_container">
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
				{{
					displayedItem?.type === "blueprint" ? "Blueprint" : "Page"
				}}:
			</span>
			<div>
				{{ displayedItem?.key ?? displayedItem?.id }}
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
import { isPlatformMac } from "@/core/detectPlatform";
import { useWriterTracking } from "@/composables/useWriterTracking";

const wf = inject(injectionKeys.core);
const wfbm = inject(injectionKeys.builderManager);

const tracking = useWriterTracking(wf);

const displayedItem = computed(() => wf.getCurrentPageInPageStack());

const selectedItemKey = computed(() => {
	if (wfbm.selection.value.length > 1) return null;

	const { component, definition: def } = useComponentInformation(
		wf,
		wfbm.firstSelectedId,
	);
	if (!component.value || component.value.type === "blueprints_blueprint") {
		return null;
	}

	return component.value?.content?.alias || def.value?.name || "Unknown";
});

// Helper to create tooltip with shortcut
function createTooltip(
	canNavigate: boolean,
	stackItem: ReturnType<typeof wf.getPreviousPageInPageStack>,
	shortcut: string,
	direction: "previous" | "next",
) {
	if (!canNavigate) return `(${shortcut})`;
	if (!stackItem?.key) return `Go to ${direction} blueprint (${shortcut})`;
	return `${stackItem.key} (${shortcut})`;
}

const previousBlueprintTooltip = computed(() => {
	const shortcut = isPlatformMac() ? "⌃-" : "Ctrl+-";
	return createTooltip(
		wf.canGoBackInPageStack(),
		wf.getPreviousPageInPageStack(),
		shortcut,
		"previous",
	);
});

const nextBlueprintTooltip = computed(() => {
	const shortcut = isPlatformMac() ? "⌃⇧-" : "Ctrl+Shift+-";
	return createTooltip(
		wf.canGoForwardInPageStack(),
		wf.getNextPageInPageStack(),
		shortcut,
		"next",
	);
});

function handleNavigateInPageStack(
	direction: "forward" | "backward",
	event: MouseEvent | KeyboardEvent,
) {
	const canNavigate =
		direction === "forward"
			? wf.canGoForwardInPageStack()
			: wf.canGoBackInPageStack();

	if (!canNavigate) return;

	event.preventDefault();
	event.stopPropagation();

	wfbm.setSelection(null);

	const stackItem = wf.navigateInPageStack(null, direction);
	if (stackItem) {
		wfbm.mode.value = stackItem.type === "blueprint" ? "blueprints" : "ui";
		wfbm.setSelection(stackItem.id, undefined, "click");
		tracking.track("blueprints_navigation_stack_clicked", {
			direction,
			source: event instanceof MouseEvent ? "click" : "keyboard",
		});
	}
}

function handleNextBlueprint(ev: MouseEvent | KeyboardEvent) {
	handleNavigateInPageStack("forward", ev);
}

function handlePreviousBlueprint(ev: MouseEvent | KeyboardEvent) {
	handleNavigateInPageStack("backward", ev);
}

function handleKeyboardShortcut(event: KeyboardEvent) {
	if (!event.ctrlKey) return;

	// Ctrl+- - Go back
	if (!event.shiftKey && event.key === "-") {
		handlePreviousBlueprint(event);
	}
	// Ctrl+Shift+- - Go forward (Shift+- produces "_" on most keyboards)
	else if (event.shiftKey && (event.key === "_" || event.key === "-")) {
		handleNextBlueprint(event);
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
	background: var(--wdsColorGray0);
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
	padding: 8px;
	border-top: 1px solid var(--wdsColorGray0);
	border-bottom: 1px solid var(--builderAreaSeparatorColor);
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
