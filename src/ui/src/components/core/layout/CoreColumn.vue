<template>
	<div
		class="CoreColumn"
		:style="rootStyle"
		:class="{
			sticky: isSticky,
			collapsible: isCollapsible,
			collapsibleToRight: isCollapsibleToRight,
			collapsed: isCollapsed,
		}"
	>
		<div v-if="fields.title.value || isCollapsible" class="header">
			<div v-if="!isCollapsed" class="titleContainer">
				<h3 v-if="fields.title.value">{{ fields.title.value }}</h3>
			</div>
			<BaseCollapseButton
				v-if="isCollapsible"
				v-model="isCollapsed"
				class="collapser"
				:direction="collapseDirection"
			/>
		</div>
		<div v-if="isCollapsed && fields.title.value" class="collapsedTitle">
			<div class="transformed">
				<div class="content">{{ fields.title.value }}</div>
			</div>
		</div>
		<BaseContainer
			class="container"
			:aria-expanded="isCollapsible ? isCollapsed : null"
			:content-h-align="fields.contentHAlign.value"
			:content-v-align="fields.contentVAlign.value"
			:content-padding="fields.contentPadding.value"
		>
			<slot></slot>
		</BaseContainer>
	</div>
</template>

<script lang="ts">
import { FieldCategory, FieldType } from "@/writerTypes";
import {
	contentHAlign,
	contentPadding,
	contentVAlign,
	cssClasses,
	separatorColor,
	startCollapsed,
	isCollapsible as isCollapsibleField,
} from "@/renderer/sharedStyleFields";

const description =
	"A layout component that organizes its child components in columns. Must be inside a Column Container component.";

export default {
	writer: {
		name: "Column",
		description,
		allowedParentTypes: ["columns", "repeater"],
		allowedChildrenTypes: ["*"],
		category: "Layout",
		fields: {
			title: {
				name: "Title",
				type: FieldType.Text,
			},
			width: {
				name: "Width (factor)",
				default: "1",
				init: "1",
				type: FieldType.Number,
				desc: "Relative size when compared to other columns in the same container. A column of width 2 will be double the width of one with width 1.",
				category: FieldCategory.Style,
			},
			isSticky: {
				name: "Sticky",
				default: "no",
				type: FieldType.Text,
				options: {
					yes: "Yes",
					no: "No",
				},
				category: FieldCategory.Style,
			},
			isCollapsible: isCollapsibleField,
			startCollapsed: {
				...startCollapsed,
				desc: "Only applied when the column is collapsible.",
			},
			separatorColor,
			contentPadding,
			contentHAlign,
			contentVAlign,
			cssClasses,
		},
	},
};
</script>
<script setup lang="ts">
import { computed, ComputedRef, inject, Ref, ref, watch } from "vue";
import injectionKeys from "@/injectionKeys";
import BaseContainer from "@/components/core/base/BaseContainer.vue";
import BaseCollapseButton from "@/components/core/base/BaseCollapseButton.vue";
import type { Direction } from "@/components/core/base/BaseCollapseButton.vue";

const instancePath = inject(injectionKeys.instancePath);
const instanceData = inject(injectionKeys.instanceData);
const wf = inject(injectionKeys.core);
const componentId = inject(injectionKeys.componentId);

const fields = inject(injectionKeys.evaluatedFields);
const isCollapsible = computed(() => fields.isCollapsible.value == "yes");
const isCollapsed: Ref<boolean> = ref(
	fields.isCollapsible.value == "yes" && fields.startCollapsed.value == "yes",
);
const isSticky = computed(() => fields.isSticky.value == "yes");

const rootStyle = computed(() => {
	let flex: string;
	if (!isCollapsed.value) {
		flex = `${fields.width.value} 0 0`;
	} else {
		flex = `0 0 32px`;
	}
	const style = {
		flex,
	};
	return style;
});

/* Collapsing direction
The minimum non-collapsible column position (mnccp) determines how other columns collapse.
Those with a position lower than mnccp collapse to the left.
Those with a position higher than mnccp collapse to the right.
*/

const isCollapsibleToRight = computed(
	() =>
		position.value >=
		columnsData.value?.value?.minimumNonCollapsiblePosition,
);

const collapseDirection = computed<Direction>(() =>
	isCollapsibleToRight.value ? "right-left" : "left-right",
);

const columnsData: ComputedRef<Ref> = computed(() => {
	for (let i = -1; i > -1 * instancePath.length; i--) {
		const item = instancePath.at(i);
		const type = wf.getComponentById(item.componentId)?.type;
		if (type !== "columns") continue;
		const columnsData = instanceData.at(i);
		return columnsData;
	}
	return null;
});

const position = computed(() => wf.getComponentById(componentId)?.position);

watch([() => fields.isCollapsible.value, position], () => {
	const cd = columnsData.value;
	if (!cd) return;
	cd.value = { minimumNonCollapsiblePosition: undefined };
});

watch(
	columnsData,
	(newColumnsData) => {
		if (!newColumnsData || !newColumnsData.value) return;
		if (isCollapsible.value) return;
		if (
			typeof newColumnsData.value.minimumNonCollapsiblePosition !==
				"undefined" &&
			position.value >= newColumnsData.value.minimumNonCollapsiblePosition
		)
			return;
		newColumnsData.value.minimumNonCollapsiblePosition = position.value;
	},
	{ immediate: true, deep: true },
);
</script>

<style scoped>
@import "@/renderer/sharedStyles.css";

.CoreColumn {
	min-width: 0;
	align-self: stretch;
	display: flex;
	flex-direction: column;
	gap: 16px;
}

.CoreColumn.sticky {
	position: sticky;
	top: 16px;
	align-self: flex-start;
}

.CoreColumn > .header {
	display: flex;
	gap: 16px;
	align-items: center;
}

.CoreColumn > .header > .titleContainer {
	flex: 1 0 0;
	order: 1;
}

.CoreColumn.collapsible.collapsibleToRight > .header > .titleContainer {
	order: 3;
	text-align: right;
}

.CoreColumn > .header > .collapser {
	order: 2;
	flex: 0 0 32px;
}

.CoreColumn.collapsibleToRight > .header {
	justify-content: left;
}

.CoreColumn > .container {
	flex: 1 0 0;
	align-self: stretch;
	display: flex;
}

.CoreColumn.collapsible.collapsed > .container {
	display: none;
}

.CoreColumn > .collapsedTitle {
	padding-top: 8px;
	opacity: 0.5;
	min-height: 200px;
	overflow: hidden;
}

.CoreColumn > .collapsedTitle > .transformed {
	transform: rotate(90deg);
}

.CoreColumn > .collapsedTitle > .transformed > .content {
	width: 200px;
	color: var(--primaryTextColor);
	white-space: nowrap;
	font-size: 0.9rem;
	text-overflow: ellipsis;
	overflow: hidden;
}

@media only screen and (max-width: 768px) {
	.CoreColumn {
		min-width: 100%;
	}

	.CoreColumn.sticky {
		position: static;
	}
}
</style>
