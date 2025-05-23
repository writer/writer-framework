<template>
	<div ref="rootEl" class="CorePage">
		<div class="sidebarContainer">
			<slot slot-name="sidebar" :positionless-slot="true"></slot>
		</div>
		<div
			class="main"
			:class="{
				compact: fields.pageMode.value == 'compact',
				wide: fields.pageMode.value == 'wide',
			}"
			data-writer-container
		>
			<slot></slot>
		</div>
	</div>
</template>

<script lang="ts">
import { FieldCategory, FieldType } from "@/writerTypes";
import {
	accentColor,
	buttonColor,
	buttonShadow,
	buttonTextColor,
	containerBackgroundColor,
	containerShadow,
	cssClasses,
	emptinessColor,
	primaryTextColor,
	secondaryTextColor,
	separatorColor,
} from "@/renderer/sharedStyleFields";
import { onMounted } from "vue";
import { getKeydown } from "@/renderer/syntheticEvents";
import { useAbortController } from "@/composables/useAbortController";

const ssKeydownStub = `
def handle_keydown(state, payload):
	# The payload is a dictionary containing the key code and modifier keys.
	# For example,
	# {
	#	"key": "ArrowDown",
	#	"ctrl_key": False,
	#	"shift_key": False,
	#	"meta_key": False
	# }

	key_activated = payload.get("key")
	delta = 0
	if key_activated == "ArrowLeft":
		delta += -10
	elif key_activated == "ArrowRight":
		delta += 10

	shift_key = payload.get("shift_key")
	if shift_key:
		delta *= 2 # Shift makes it go faster

	state["position"] += delta
`;

const ssPageOpenStub = `
def handle_page_open(state, payload):
	page_key = payload
	state["message"] = f"The page {page_key} has been opened."
`;

const description =
	"A container component representing a single page within the application.";

export default {
	writer: {
		name: "Page",
		category: "Root",
		events: {
			"wf-keydown": {
				desc: "Captures all key activity while this page is open.",
				stub: ssKeydownStub,
			},
			"wf-page-open": {
				desc: "Emitted when the page is opened.",
				stub: ssPageOpenStub,
			},
		},
		description,
		allowedChildrenTypes: ["*"],
		allowedParentTypes: ["root"],
		fields: {
			key: {
				name: "Page key",
				desc: "Unique identifier. It's needed to enable navigation to this Page.",
				type: FieldType.IdKey,
			},
			pageMode: {
				name: "Page mode",
				default: "compact",
				type: FieldType.Text,
				options: {
					compact: "Compact",
					wide: "Wide",
				},
				category: FieldCategory.Style,
			},
			accentColor,
			primaryTextColor,
			secondaryTextColor,
			emptinessColor,
			containerBackgroundColor,
			containerShadow,
			separatorColor,
			buttonColor,
			buttonTextColor,
			buttonShadow,
			cssClasses,
		},
		previewField: "key",
	},
};
</script>
<script setup lang="ts">
import { inject, useTemplateRef, watch } from "vue";
import injectionKeys from "@/injectionKeys";

const rootEl = useTemplateRef("rootEl");
const fields = inject(injectionKeys.evaluatedFields);
const wfbm = inject(injectionKeys.builderManager);
const notesManager = inject(injectionKeys.notesManager);

const abort = useAbortController();

function handleMousedown(ev: MouseEvent) {
	const target = ev.target;
	if (!(target instanceof Element)) return;
	if (target.closest("[data-writer-unselectable]")) return;

	const targetEl = target.closest("[data-writer-id]");
	const targetId = (targetEl as HTMLElement)?.dataset.writerId;
	if (!targetId) return;

	// @ts-expect-error get dataset prop
	const targetInstancePath = targetEl.dataset?.writerInstancePath;

	if (notesManager.isAnnotating.value && wfbm.mode.value !== "preview") {
		ev.preventDefault();
		notesManager.createNote(targetId, { instancePath: targetInstancePath });
	}
}

function handleKeydown(ev: KeyboardEvent) {
	const ssEv = getKeydown(ev);
	const targetEl = ev.target as HTMLElement;
	if (!rootEl.value.contains(targetEl)) return;
	rootEl.value.dispatchEvent(ssEv);
}

function emitPageOpenEvent() {
	const payload = fields.key.value;
	const event = new CustomEvent("wf-page-open", {
		detail: {
			payload,
		},
	});
	rootEl.value.dispatchEvent(event);
}

watch(rootEl, () => {
	if (!rootEl.value) return;
	rootEl.value.addEventListener("mousedown", handleMousedown, {
		signal: abort.signal,
	});
});

onMounted(async () => {
	document.addEventListener("keydown", handleKeydown, {
		signal: abort.signal,
	});
	emitPageOpenEvent();
});
</script>

<style scoped>
@import "@/renderer/sharedStyles.css";

.CorePage {
	display: flex;
	width: 100%;
	min-height: 100%;
	background: var(--emptinessColor);
	flex: 1 0 auto;
	flex-direction: row;
	align-items: stretch;
}

.sidebarContainer {
	display: flex;
	flex: 0 1 0;
	align-self: stretch;
}

.main {
	flex: 1 0 0;
	padding: 16px;
	min-width: 0;
}

.childless .main {
	background: var(--emptinessColor) !important;
}
.childless .main::after {
	content: "Empty Page. Drag and drop components from the Toolkit to get started." !important;
}
.main.compact {
	width: 100%;
	max-width: 1200px;
	margin-left: auto;
	margin-right: auto;
}
.main.wide {
	width: 100%;
}

@media only screen and (max-width: 768px) {
	.CorePage {
		flex-direction: column;
	}
}
</style>
