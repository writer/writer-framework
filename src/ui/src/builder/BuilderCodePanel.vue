<template>
	<BuilderPanel name="Code" :actions="actions" class="BuilderCodePanel">
		<BuilderEmbeddedCodeEditor
			variant="full"
			language="python"
			v-model="code"
			:key="Array.from(wfbm.openPanels).join('-')"
		></BuilderEmbeddedCodeEditor>
	</BuilderPanel>
</template>

<script setup lang="ts">
import { inject, ref } from "vue";
import BuilderEmbeddedCodeEditor from "./BuilderEmbeddedCodeEditor.vue";
import BuilderPanel, { type BuilderPanelAction } from "./BuilderPanel.vue";
import injectionKeys from "@/injectionKeys";

const wf = inject(injectionKeys.core);

const wfbm = inject(injectionKeys.builderManager);
const code = ref<string>(wf.runCode.value);

const actions: BuilderPanelAction[] = [
	{
		icon: "save",
		callback: () => {
			wfbm.openPanels.delete("code");
		},
	},
	{
		icon: "close",
		callback: () => {
			wfbm.openPanels.delete("code");
		},
	},
];
</script>

<style scoped>
@import "./sharedStyles.css";
</style>
