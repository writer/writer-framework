<template>
	<div
		class="BuilderPanelSwitcher"
		:class="{ openPanels: wfbm.openPanels.value.size > 0 }"
	>
		<div ref="screenEl" class="screen"></div>
		<div class="switches">
			<BuilderCodePanel
				:contents-teleport-el="screenEl"
			></BuilderCodePanel>
			<BuilderLogPanel :contents-teleport-el="screenEl"></BuilderLogPanel>
		</div>
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
import injectionKeys from "@/injectionKeys";
import { inject, useTemplateRef } from "vue";
import BuilderCodePanel from "./BuilderCodePanel.vue";
import BuilderLogPanel from "./BuilderLogPanel.vue";

const wfbm = inject(injectionKeys.builderManager);

const screenEl = useTemplateRef("screenEl");
</script>

<style scoped>
.BuilderPanelSwitcher {
	display: grid;
	background: var(--builderBackgroundColor);
	grid-template-rows: 48px;
	grid-template-columns: 1fr;
	z-index: 1; /* makes sure it's on top of `.ComponentRenderer` */
}

.BuilderPanelSwitcher.openPanels {
	grid-template-rows: 1fr 48px;
}

.screen {
	display: none;
	grid-template-columns: repeat(auto-fit, minmax(50%, 1fr));
	grid-template-rows: 1fr;
	overflow: hidden;
}

.openPanels .screen {
	display: grid;
}

.screen:deep(> *) {
	border-left: 1px solid var(--builderSeparatorColor);
	border-top: 1px solid var(--builderIntenseSeparatorColor);
}

.screen:deep(> *:first-child:last-child) {
	border-left: none;
}

.screen:deep(> *:not([data-order="1"])) {
	border-left: none;
}

.switches {
	border-top: 1px solid var(--builderIntenseSeparatorColor);
	display: flex;
	align-items: center;
	justify-content: space-between;
	padding: 0 16px 0 8px;
}

.openPanels .switches {
	border-top: 1px solid var(--builderSeparatorColor);
}
</style>
