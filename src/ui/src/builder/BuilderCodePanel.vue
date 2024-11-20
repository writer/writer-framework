<template>
	<BuilderPanel name="Code" :actions="actions" class="BuilderCodePanel">
		<BuilderEmbeddedCodeEditor
			:key="Array.from(wfbm.openPanels).join('-')"
			v-model="code"
			variant="full"
			language="python"
			:disabled="isDisabled"
			@update:model-value="handleUpdate"
		></BuilderEmbeddedCodeEditor>
		<template #actionsCompanion>
			<div v-if="status" class="status" :class="status.type">
				{{ status.message }}
			</div>
		</template>
	</BuilderPanel>
</template>

<script setup lang="ts">
import { computed, defineAsyncComponent, inject, ref, watch } from "vue";
import BuilderPanel, { type BuilderPanelAction } from "./BuilderPanel.vue";
import BuilderAsyncLoader from "./BuilderAsyncLoader.vue";
import injectionKeys from "@/injectionKeys";

const BuilderEmbeddedCodeEditor = defineAsyncComponent({
	loader: () => import("./BuilderEmbeddedCodeEditor.vue"),
	loadingComponent: BuilderAsyncLoader,
});

const wf = inject(injectionKeys.core);

const wfbm = inject(injectionKeys.builderManager);
const code = ref<string>(wf.runCode.value);
const status = ref<null | {
	type: "error" | "success" | "neutral";
	message: string;
}>(null);
const isDisabled = ref<boolean>(false);

const actions = computed<BuilderPanelAction[]>(() => [
	{
		icon: "save",
		name: "Save and run",
		keyboardShortcut: {
			modifierKey: true,
			key: "S",
		},
		callback: () => {
			save();
		},
		isDisabled: isDisabled.value,
	},
	{
		icon: "close",
		name: "Close",
		keyboardShortcut: {
			modifierKey: false,
			key: "Escape",
		},
		callback: () => {
			wfbm.openPanels.delete("code");
		},
	},
]);

watch(wf.runCode, (newRunCode) => {
	code.value = newRunCode;
});

watch(wf.sessionTimestamp, () => {
	isDisabled.value = false;
	if (isCodeSaved()) return;
	status.value = null;
});

function handleUpdate() {
	status.value = null;
}

function isCodeSaved() {
	return wf.runCode.value == code.value;
}

async function save() {
	status.value = {
		type: "neutral",
		message: "Processing...",
	};
	try {
		isDisabled.value = true;
		await wf.sendCodeSaveRequest(code.value);
	} catch {
		status.value = {
			type: "error",
			message: "Code hasn't been saved.",
		};
		isDisabled.value = false;
		return;
	}
	status.value = {
		type: "success",
		message: "Saved.",
	};
}
</script>

<style scoped>
@import "./sharedStyles.css";

.status {
	padding: 2px 12px 2px 12px;
	border-radius: 16px;
	font-size: 12px;
}

.status.success,
.status.neutral {
	border: 1px solid var(--builderSeparatorColor);
	background: var(--builderSubtleSeparatorColor);
}

.status.error {
	border: 1px solid #ffcfc2;
	background: #fff4f1;
}
</style>
