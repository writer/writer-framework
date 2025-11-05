<template>
	<div ref="rootInstance" class="CoreTabs">
		<nav
			class="tabSelector horizontal"
			data-writer-cage
			data-writer-container
		>
			<slot :instance-number="0"></slot>
		</nav>
		<div class="container">
			<slot :instance-number="1"></slot>
		</div>
	</div>
</template>

<script lang="ts">
import {
	accentColor,
	primaryTextColor,
	secondaryTextColor,
	containerBackgroundColor,
	containerShadow,
	separatorColor,
	buttonColor,
	buttonTextColor,
	buttonShadow,
	cssClasses,
} from "@/renderer/sharedStyleFields";
import { useFormValueBroker } from "@/renderer/useFormValueBroker";

const tabChangeHandlerStub = `
def tab_change_handler(state, payload):

	# The payload contains the name of the newly activated tab

	state["active_tab"] = payload`;

const description =
	"A container component for organising and displaying Tab components in a tabbed interface.";

export default {
	writer: {
		name: "Tab container",
		description,
		category: "Layout",
		allowedChildrenTypes: ["tab", "repeater"],
		events: {
			"wf-tab-change": {
				desc: "Sent when the active tab changes.",
				stub: tabChangeHandlerStub.trim(),
				eventPayloadExample: "Tab Name",
				bindable: true,
			},
		},
		fields: {
			accentColor,
			primaryTextColor,
			secondaryTextColor,
			containerBackgroundColor,
			containerShadow,
			separatorColor,
			buttonColor,
			buttonTextColor,
			buttonShadow,
			cssClasses,
		},
	},
};
</script>
<script setup lang="ts">
import { ComponentPublicInstance, inject, onMounted, ref, watch } from "vue";
import { useEvaluator } from "@/renderer/useEvaluator";
import injectionKeys from "@/injectionKeys";
const rootInstance = ref<ComponentPublicInstance | null>(null);
const wf = inject(injectionKeys.core);
const instancePath = inject(injectionKeys.instancePath);
const instanceData = inject(injectionKeys.instanceData);
const containerState = instanceData.at(-1);
const { isComponentVisible } = useEvaluator(wf);

const { formValue, handleInput } = useFormValueBroker(
	wf,
	instancePath,
	rootInstance,
);

containerState.value = {
	activeTab: undefined,
	activeTabName: formValue.value,
	tabs: [],
};

watch(
	() => containerState.value?.activeTabName,
	(activeTabName) => {
		if (!rootInstance.value) return;
		if (activeTabName === formValue.value) return;
		handleInput(activeTabName, "wf-tab-change");
	},
);

watch(formValue, (newTabName) => {
	if (newTabName === containerState.value.activeTabName) return;
	if (!containerState.value.tabs?.length) return;

	const visibleTabs = containerState.value.tabs.filter((t) =>
		isComponentVisible(t.componentId, t.instancePath),
	);
	if (!visibleTabs.length) return;

	let tabToActivate = visibleTabs.find((t) => t.name === newTabName);

	if (!tabToActivate) {
		const currentActiveInState = visibleTabs.find(
			(t) => t.name === containerState.value.activeTabName,
		);
		tabToActivate = currentActiveInState ?? visibleTabs[0];
	}

	containerState.value.activeTab = tabToActivate.instancePath;
	containerState.value.activeTabName = tabToActivate.name;
});

onMounted(() => {
	if (containerState.value.activeTab) return;
	if (!containerState.value.tabs) return;

	const visibleTabs = containerState.value.tabs.filter((t) =>
		isComponentVisible(t.componentId, t.instancePath),
	);
	if (visibleTabs.length === 0) return;

	const initialActiveTabName = containerState.value.activeTabName;
	const tabToActivate =
		visibleTabs.find((t) => t.name === initialActiveTabName) ??
		visibleTabs[0];

	containerState.value.activeTab = tabToActivate.instancePath;
	containerState.value.activeTabName = tabToActivate.name;
});
</script>

<style scoped>
@import "@/renderer/sharedStyles.css";
@import "@/renderer/colorTransformations.css";

.CoreTabs {
	width: 100%;
	background: var(--containerBackgroundColor);
	border-radius: 8px;
	box-shadow: var(--containerShadow);
	border: 1px solid var(--separatorColor);
}

.tabSelector {
	pointer-events: all;
	color: var(--secondaryTextColor);
	max-width: 100%;
	overflow-x: auto;
	border-bottom: 1px solid var(--separatorColor);
	display: flex;
	gap: 24px;
	padding: 0 16px 0 16px;
}

.childless > .tabSelector {
	display: none;
}

.container {
	background: var(--containerBackgroundColor);
	border-bottom-left-radius: 8px;
	border-bottom-right-radius: 8px;
}

.childless > .container {
	border-radius: 8px;
	border: none;
}
</style>
