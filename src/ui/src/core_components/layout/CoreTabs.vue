<template>
	<div class="CoreTabs">
		<nav
			class="tabSelector horizontal"
			data-streamsync-cage
			data-streamsync-container
		>
			<div class="tabSelectorInner">
				<slot :instance-number="0"></slot>
			</div>
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
} from "../../renderer/sharedStyleFields";

const description =
	"A container component for organising and displaying Tab components in a tabbed interface.";

export default {
	streamsync: {
		name: "Tab Container",
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
import injectionKeys from "../../injectionKeys";

const instanceData = inject(injectionKeys.instanceData);
instanceData.at(-1).value = { activeTab: undefined };
</script>

<style scoped>
@import "../../renderer/sharedStyles.css";

.CoreTabs {
	width: 100%;
}

.tabSelector {
	pointer-events: all;
	border-radius: 8px 8px 0 0;
	background: var(--containerBackgroundColor);
	width: fit-content;
	color: var(--secondaryTextColor);
	max-width: 100%;
	overflow-x: auto;
	box-shadow: var(--containerShadow);
	border-top: 1px solid var(--separatorColor);
	border-left: 1px solid var(--separatorColor);
	border-right: 1px solid var(--separatorColor);
}

.tabSelectorInner {
	display: flex;
	gap: 16px;
	padding: 0 16px 0 16px;
	background: var(--containerBackgroundColor);
}

.childless > .tabSelector {
	display: none;
}

.container {
	background: var(--containerBackgroundColor);
	border-radius: 0 8px 8px 8px;
	box-shadow: var(--containerShadow);
	border: 1px solid var(--separatorColor);
}

.childless > .container {
	border-radius: 8px;
	border: none;
}
</style>
