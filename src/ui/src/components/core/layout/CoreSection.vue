<template>
	<section
		class="CoreSection"
		:class="{ 'CoreSection--collapsible': isCollapsible }"
	>
		<div
			v-if="fields.title.value || isCollapsible"
			class="CoreSection__title"
			:class="{
				'CoreSection__title--collapsed': isCollapsible && isCollapsed,
			}"
		>
			<h3>{{ fields.title.value }}</h3>
			<button
				v-if="isCollapsible"
				role="button"
				class="CoreSection__title__collapser"
				@click="isCollapsed = !isCollapsed"
			>
				<i class="material-symbols-outlined">keyboard_arrow_up</i>
			</button>
		</div>
		<BaseContainer
			v-if="!isCollapsed"
			:content-h-align="fields.contentHAlign.value"
			:content-padding="fields.contentPadding.value"
			:aria-expanded="isCollapsible ? 'true' : null"
		>
			<slot></slot>
		</BaseContainer>
	</section>
</template>

<script lang="ts">
import { FieldType } from "@/writerTypes";
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
	isCollapsible as isCollapsibleField,
	startCollapsed,
} from "@/renderer/sharedStyleFields";

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
				init: "Section Title",
				desc: "Leave blank to hide.",
				type: FieldType.Text,
			},
			isCollapsible: isCollapsibleField,
			startCollapsed,
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
import { computed, inject, ref } from "vue";
import injectionKeys from "@/injectionKeys";
import BaseContainer from "../base/BaseContainer.vue";

const fields = inject(injectionKeys.evaluatedFields);

const isCollapsible = computed(() => fields.isCollapsible.value === "yes");
const isCollapsed = ref<boolean>(
	isCollapsible.value && fields.startCollapsed.value === "yes",
);
</script>

<style scoped>
@import "@/renderer/sharedStyles.css";
.CoreSection {
	border: 1px solid var(--separatorColor);
	border-radius: 8px;
	box-shadow: var(--containerShadow);
	background-color: var(--containerBackgroundColor);
}

.CoreSection__title {
	margin: 16px 16px 0 16px;
	display: grid;
	grid-template-columns: 1fr auto;
}
.CoreSection__title--collapsed {
	margin: 16px;
}

.CoreSection__title--collapsed .CoreSection__title__collapser {
	transform: rotate(180deg);
}

.CoreSection__title__collapser {
	border: none;
	border-radius: 50%;
	padding: 4px;
	background: var(--separatorColor);
	display: flex;
	align-items: center;
	justify-content: center;

	height: 24px;
	width: 24px;
	cursor: pointer;
}

.CoreSection__title__collapser {
	transition: all 0.3s ease-in-out;
	transform: rotate(0deg);
}
</style>
