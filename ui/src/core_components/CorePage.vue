<template>
	<div class="CorePage">
		<div class="sidebarContainer">
			<slot
				:component-filter="(c: Component) => c.type == 'sidebar'"
				:positionless-slot="true"
			></slot>
		</div>
		<div
			class="main"
			:class="{
				compact: fields.pageMode.value == 'compact',
				wide: fields.pageMode.value == 'wide',
			}"
			data-streamsync-container
		>
			<slot
				:component-filter="(c: Component) => c.type != 'sidebar'"
			></slot>
		</div>
	</div>
</template>

<script lang="ts">
import { Component, FieldCategory, FieldType } from "../streamsyncTypes";
import * as sharedStyleFields from "../renderer/sharedStyleFields";

const description =
	"A container component representing a single page within the application.";

export default {
	streamsync: {
		name: "Page",
		category: "Root",
		description,
		allowedChildrenTypes: ["*"],
		allowedParentTypes: ["root"],
		fields: {
			key: {
				name: "Page key",
				desc: "Unique identifier. It's needed to enable navigation to this Page.",
				type: FieldType.IdKey,
			},
			pageMode: {
				name: "Page mode",
				default: "compact",
				type: FieldType.Text,
				options: {
					compact: "Compact",
					wide: "Wide",
				},
				category: FieldCategory.Style,
			},
			...sharedStyleFields,
		},
		previewField: "key",
	},
};
</script>
<script setup lang="ts">
import { inject } from "vue";
import injectionKeys from "../injectionKeys";

const fields = inject(injectionKeys.evaluatedFields);
</script>

<style scoped>
@import "../renderer/sharedStyles.css";

.CorePage {
	display: flex;
	width: 100%;
	min-height: 100%;
	background: var(--emptinessColor);
	flex: 1 0 auto;
	flex-direction: row;
	align-items: stretch;
}

.sidebarContainer {
	display: flex;
	flex: 0 1 0;
	align-self: stretch;
}

.main {
	flex: 1 0 0;
	padding: 16px;
	min-width: 0;
}

.childless .main {
	background: var(--emptinessColor) !important;
}
.childless .main::after {
	content: "Empty Page. Drag and drop components from the Toolkit to get started." !important;
}
.main.compact {
	width: 100%;
	max-width: 1200px;
	margin-left: auto;
	margin-right: auto;
}
.main.wide {
	width: 100%;
}

@media only screen and (max-width: 768px) {
	.CorePage {
		flex-direction: column;
	}
}
</style>
