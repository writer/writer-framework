<template>
	<div
		class="CoreHorizontalStack horizontal"
		:class="[`justify-${fields.alignment.value}`]"
	>
		<div class="CoreHorizontalStack horizontal"
				 data-streamsync-container
				 :class="[`justify-${fields.alignment.value}`]"
				 :style="containerStyle">
			<slot></slot>
		</div>
	</div>
</template>

<script lang="ts">
import { FieldType } from "../streamsyncTypes";
import {contentWidth, cssClasses} from "../renderer/sharedStyleFields";

const description =
	"A layout component that stacks its child components horizontally, wrapping them to the next row if necessary.";

export default {
	streamsync: {
		name: "Horizontal Stack",
		description,
		allowedChildrenTypes: ["*"],
		category: "Layout",
		fields: {
			alignment: {
				name: "Alignment",
				default: "left",
				type: FieldType.Text,
				options: {
					left: "Left",
					center: "Center",
					right: "Right",
				},
			},
			contentWidth,
			cssClasses,
		},
	},
};
</script>
<script setup lang="ts">
import {computed, inject} from "vue";
import injectionKeys from "../injectionKeys";
import {contentWidth} from "../renderer/sharedStyleFields";

const fields = inject(injectionKeys.evaluatedFields);

const containerStyle = computed(() => {
	return {
		"width": fields.contentWidth.value,
	};
});
</script>

<style scoped>
@import "../renderer/sharedStyles.css";

.CoreHorizontalStack {
	display: flex;
	flex-wrap: wrap;
	flex-direction: row;
	align-items: center;
}

.justify-left {
	justify-content: left;
}
.justify-center {
	justify-content: center;
}
.justify-right {
	justify-content: right;
}
</style>
