<template>
	<div v-if="ssbm.isSelectionActive()" class="BuilderSettingsHandlers">
		<div class="BuilderSettingsHandlers__title">
			<i class="material-symbols-outlined">bolt</i>
			<h3>Events</h3>
		</div>
		<div class="BuilderSettingsHandlers__list">
			<div
				v-for="(eventInfo, eventType) in recognisedEvents"
				:key="eventType"
			>
				<div class="columns">
					<WdsFieldWrapper
						:label="eventType"
						:hint="eventInfo?.desc"
						:help-button="
							getStubCode(eventType)
								? 'Show event handler stub'
								: false
						"
						@help-click="showStub(eventType)"
					>
						<BuilderSelect
							:model-value="component.handlers?.[eventType] ?? ''"
							:options="getOptions(eventType)"
							enable-search
							@update:model-value="
								handleHandlerChange($event, eventType)
							"
						/>
					</WdsFieldWrapper>
				</div>
			</div>
			<WdsButton variant="tertiary" @click="showCustomHandlerModal">
				<i class="material-symbols-outlined">add</i>Add custom handler
			</WdsButton>
		</div>
		<BuilderModal
			v-if="stubModal"
			:close-action="stubCloseAction"
			icon="help"
			:modal-title="stubModal?.modalTitle"
		>
			<div class="stubMessage">
				You can use the following stub code as a starting point for your
				event handler.
			</div>
			<div class="codeContainer">
				<code v-dompurify-html="stubModal.highlightedCodeHtml"> </code>
			</div>
			<WdsButton
				variant="tertiary"
				@click="copyToClipboard(stubModal.code)"
			>
				<i class="material-symbols-outlined">content_copy</i>
				Copy code to clipboard
			</WdsButton>
		</BuilderModal>
		<BuilderModal
			v-if="customHandlerModal"
			:close-action="customHandlerModalCloseAction"
			icon="bolt"
			modal-title="Add Custom Event Handler"
			allow-overflow
		>
			<div class="customHandlerModalForm">
				<WdsFieldWrapper
					label="Event type"
					hint="Can be any event type."
				>
					<WdsTextInput
						v-model="customHandlerModal.eventType"
						type="text"
						list="commonEventTypes"
					/>
					<datalist id="commonEventTypes">
						<option
							v-for="commonEventType in commonEventTypes"
							:key="commonEventType"
							:value="commonEventType"
						>
							{{ commonEventType }}
						</option>
					</datalist>
				</WdsFieldWrapper>
				<WdsFieldWrapper
					label="Handler function"
					hint="The function that will handle the event."
				>
					<BuilderSelect
						v-model="customHandlerModal.handlerFunctionName"
						:options="options"
						enable-search
					/>
				</WdsFieldWrapper>
			</div>

			<WdsButton variant="tertiary" @click="addCustomEventHandler()">
				<i class="material-symbols-outlined">add</i>Add
			</WdsButton>
		</BuilderModal>
	</div>
</template>

<script setup lang="ts">
import * as monaco from "monaco-editor";

import { computed, ComputedRef, inject, Ref, ref } from "vue";
import { useComponentActions } from "../useComponentActions";
import injectionKeys from "@/injectionKeys";
import BuilderModal, { ModalAction } from "../BuilderModal.vue";
import { WriterComponentDefinition } from "@/writerTypes";
import BuilderSelect from "../BuilderSelect.vue";
import type { Option } from "../BuilderSelect.vue";
import WdsFieldWrapper from "@/wds/WdsFieldWrapper.vue";
import WdsTextInput from "@/wds/WdsTextInput.vue";
import WdsButton from "@/wds/WdsButton.vue";

const wf = inject(injectionKeys.core);
const ssbm = inject(injectionKeys.builderManager);

const { setHandlerValue } = useComponentActions(wf, ssbm);
const component = computed(() => wf.getComponentById(ssbm.getSelectedId()));

const options = computed<Option[]>(() => {
	const userFunctionsOptions: Option[] = userFunctions.value
		.map((v) => v.name)
		.map((v) => ({ value: v, label: v, icon: "function" }));

	const pageKeyOptions: Option[] = pageKeys.value.map((v) => ({
		label: `Go to page "${v}"`,
		value: `$goToPage_${v}`,
		icon: "link",
	}));

	const workflowKeyOptions: Option[] = workflowKeys.value.map((v) => ({
		label: `Run workflow "${v}"`,
		value: `$runWorkflow_${v}`,
		icon: "linked_services",
	}));

	return [
		{ label: "(No handler)", value: "", icon: "block" },
		...userFunctionsOptions,
		...pageKeyOptions,
		...workflowKeyOptions,
	];
});

function getOptions(eventType?: string): Option[] {
	if (!isHandlerInvalid(eventType)) return options.value;

	const handler = component.value.handlers?.[eventType];

	return [
		...options.value,
		{ value: handler, label: `${handler} (Not found)` },
	];
}

const recognisedEvents: ComputedRef<WriterComponentDefinition["events"]> =
	computed(() => {
		const { type } = component.value;
		const { events: supportedEvents } = wf.getComponentDefinition(type);

		const recEvents = { ...supportedEvents };

		Object.keys({ ...component.value.handlers }).forEach((eventType) => {
			if (recEvents[eventType]) return;
			recEvents[eventType] = { desc: "Custom event" };
		});

		return recEvents;
	});

const userFunctions = wf.userFunctions;

const pageKeys = computed(() => {
	const pages = wf.getComponents("root");
	const pageKeys = pages
		.filter((page) => page.type == "page")
		.map((page) => page.content["key"])
		.filter((pageKey) => Boolean(pageKey));
	return pageKeys;
});

const workflowKeys = computed(() => {
	const workflows = wf.getComponents("workflows_root");
	const workflowKeys = workflows
		.filter((workflow) => workflow.type == "workflows_workflow")
		.map((workflow) => workflow.content["key"])
		.filter((workflowKey) => Boolean(workflowKey));
	return workflowKeys;
});

const isHandlerInvalid = (eventType: string) => {
	const handlerFunctionName = component.value.handlers?.[eventType];
	if (!handlerFunctionName) return false;

	// $ is reserved for frontend internal use, such as page change

	if (handlerFunctionName.startsWith("$")) {
		return false;
	}
	if (userFunctions.value.some((uf) => uf.name == handlerFunctionName))
		return false;
	return true;
};

const handleHandlerChange = (functionName: string, eventType: string) => {
	setHandlerValue(component.value.id, eventType, functionName);
};

type StubModal = {
	code: string;
	highlightedCodeHtml: string;
	modalTitle: string;
};

type CustomHandlerModal = {
	eventType: string;
	handlerFunctionName: string;
};

const stubModal: Ref<StubModal> = ref(null);
const customHandlerModal: Ref<CustomHandlerModal> = ref(null);

function getCustomEventStubCode() {
	return `
# When dealing with a DOM event, Writer Framework generates a payload by serialising its
# primitive properties (non-Object, non-function properties).

# If the event is instead an instance of CustomEvent,
# it looks for a "payload" property inside the CustomEvent's "detail" property. 

def handle_keydown(state, payload):
	print(payload) # Shows all the properties captured

	key_activated = payload.get("key")
	if key_activated == "ArrowLeft":
		state["position"] += -10
	elif key_activated == "ArrowRight":
		state["position"] += 10

	`;
}

function getStubCode(eventType: string) {
	const { type } = component.value;
	const { events } = wf.getComponentDefinition(type);
	const event = events?.[eventType];

	if (!event) return getCustomEventStubCode();

	return event?.stub;
}

async function showStub(eventType: string) {
	const code = getStubCode(eventType);
	const highlightedCodeHtml = await monaco.editor.colorize(
		code.trim(),
		"python",
		{},
	);
	stubModal.value = {
		modalTitle: `"${eventType}" event`,
		code,
		highlightedCodeHtml,
	};
}

const commonEventTypes = [
	"click",
	"mousedown",
	"mouseup",
	"mouseenter",
	"mouseleave",
	"mousemove",
	"keydown",
	"keyup",
	"keypress",
	"input",
	"change",
	"submit",
	"focus",
	"blur",
	"resize",
	"scroll",
	"load",
];

function addCustomEventHandler() {
	const { eventType, handlerFunctionName } = customHandlerModal.value;
	setHandlerValue(component.value.id, eventType, handlerFunctionName);
	customHandlerModal.value = null;
}

const stubCloseAction: ModalAction = {
	desc: "Close",
	fn: () => {
		stubModal.value = null;
	},
};

function showCustomHandlerModal() {
	customHandlerModal.value = {
		eventType: null,
		handlerFunctionName: null,
	};
}

const customHandlerModalCloseAction: ModalAction = {
	desc: "Close",
	fn: () => {
		customHandlerModal.value = null;
	},
};

const copyToClipboard = (text: string) => {
	navigator.clipboard.writeText(text);
};
</script>

<style scoped>
@import "../sharedStyles.css";

.BuilderSettingsHandlers {
	padding: 24px;
}

.BuilderSettingsHandlers__title {
	padding-bottom: 24px;
	display: flex;
	gap: 8px;
	align-items: center;
	font-size: 1rem;
}

.BuilderSettingsHandlers__list {
	display: flex;
	flex-direction: column;
	gap: 24px;
}

.addHandler .fields {
	display: flex;
	gap: 16px;
	margin-bottom: 16px;
}

.stubMessage {
	font-size: 0.8rem;
}

.codeContainer {
	white-space: pre-wrap;
	background: var(--builderSubtleHighlightColorSolid);
	padding: 16px;
	border-radius: 4px;
	font-family: Consolas, monospace;
	font-size: 0.85rem;
	margin-top: 12px;
	margin-bottom: 12px;
	overflow: hidden;
	text-overflow: ellipsis;
}

.codeContainer code {
	white-space: pre-wrap;
}

.customHandlerModalForm {
	display: grid;
	grid-template-columns: 1fr 1fr;
	align-items: center;
	gap: 16px;
	margin-bottom: 16px;
}
</style>
