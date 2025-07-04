<template>
	<div class="CoreTabs">
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

const description =
	"A container component for organising and displaying Tab components in a tabbed interface.";

export default {
	writer: {
		name: "Tab container",
		description,
		category: "Layout",
		allowedChildrenTypes: ["tab", "repeater"],
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
import { inject } from "vue";
import injectionKeys from "@/injectionKeys";

const instanceData = inject(injectionKeys.instanceData);
instanceData.at(-1).value = { activeTab: undefined };
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
