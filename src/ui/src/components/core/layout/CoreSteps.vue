<template>
	<div class="CoreSteps">
		<nav
			class="stepSelector horizontal"
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
	"A container component for displaying Step components, allowing you to implement a stepped blueprint.";

export default {
	writer: {
		name: "Step Container",
		description,
		category: "Layout",
		allowedChildrenTypes: ["step", "repeater"],
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
import { InstancePath } from "@/writerTypes";

export type StepsData = {
	activeStep: InstancePath;
	steps: {
		instancePath: InstancePath;
		isCompleted: string;
	}[];
};

const instanceData = inject(injectionKeys.instanceData);

const stepsData: StepsData = {
	activeStep: undefined,
	steps: [],
};

instanceData.at(-1).value = stepsData;
</script>

<style scoped>
@import "@/renderer/sharedStyles.css";

.CoreSteps {
	width: 100%;
	border: 1px solid var(--separatorColor);
	border-radius: 8px;
	background: var(--containerBackgroundColor);
	box-shadow: var(--containerShadow);
}

.stepSelector {
	pointer-events: all;
	display: flex;
	gap: 0;
	color: var(--secondaryTextColor);
	padding: 0 16px 0 16px;
	max-width: 100%;
	overflow-x: auto;
	justify-content: center;
}

.childless > .stepSelector {
	display: none;
}

.container {
	background: var(--containerBackgroundColor);
	border-bottom-left-radius: 8px;
	border-bottom-right-radius: 8px;
}

.childless > .container {
	border: none;
}
</style>
