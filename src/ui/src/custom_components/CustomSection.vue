<template>
	<section class="CoreSection">
		<h3 v-if="fields.title.value">{{ fields.title.value }}</h3>
		<BaseContainer
			v-on:click.capture="captureClick"
			:content-h-align="fields.contentHAlign.value"
			:content-padding="fields.contentPadding.value"
		>
			<slot></slot>
		</BaseContainer>
	</section>
</template>

<script lang="ts">
import { FieldType } from "../writerTypes";
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
	contentHAlign,
	contentPadding,
} from "../renderer/sharedStyleFields";

const description =
	"A container component that divides the layout into sections, with an optional title.";


	export default {
	writer: {
		name: "Section",
		description,
		category: "Layout",
		allowedChildrenTypes: ["*"],
		fields: {
			title: {
				name: "Title",
				init: "Custom Section Title",
				desc: "Leave blank to hide.",
				type: FieldType.Text,
			},
			accentColor,
			primaryTextColor,
			secondaryTextColor,
			containerBackgroundColor,
			containerShadow,
			separatorColor,
			buttonColor,
			buttonTextColor,
			buttonShadow,
			contentPadding: {
				...contentPadding,
				default: "16px",
			},
			contentHAlign,
			cssClasses,
		},
		previewField: "title",
	},
};
</script>

<script setup lang="ts">
import { inject } from "vue";
import injectionKeys from "../injectionKeys";
import BaseContainer from "../core_components/base/BaseContainer.vue";

const fields = inject(injectionKeys.evaluatedFields);
const wf = inject(injectionKeys.core);
const instancePath = inject(injectionKeys.instancePath);
const ignoreClickComponents = ["tab"]

function captureClick(event: Event) {
	const targetElement: HTMLElement = (event.target as HTMLElement).closest(
		"[data-writer-id]"
	);

	//fail early and permit normal behavior for tabs
	if (clickIsOnATab(targetElement)) return
	
    event.stopPropagation()

	if (clickIsNotOnAButton(targetElement)) { return }
	// if (buttonsDisabled) { return }

	const customId = getComponentCustomId(targetElement)
	console.log('customId: ' + customId)
	const customEvent = new CustomEvent("click", {
		detail: {
			payload: {
				id: customId,
			},
		},
	});
	wf.forwardEvent(customEvent, instancePath, true)
}

function getComponentCustomId(targetElement: HTMLElement): string {
	var component = wf.getComponentById(targetElement.dataset.writerId)
	var customId = component.content["customId"]
	var defaultId = targetElement.dataset.writerId

	return (customId != "") ? customId : defaultId
}

function clickIsOnATab(targetElement): boolean {
	var component = wf.getComponentById(targetElement.dataset.writerId)
	return "tab" == component["type"]
}


function clickIsNotOnAButton(targetElement: HTMLElement): boolean {
    return "BUTTON" != targetElement.nodeName	
}

</script>

<style scoped>
@import "../renderer/sharedStyles.css";
.CoreSection {
	overflow: hidden;
	border: 1px solid var(--separatorColor);
	border-radius: 8px;
	box-shadow: var(--containerShadow);
	background-color: var(--containerBackgroundColor);
}

h3 {
	margin: 16px 16px 0 16px;
}
</style>
