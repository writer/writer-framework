<template>
	<div class="CoreColumns horizontal" data-streamsync-container>
		<slot></slot>
	</div>
</template>

<script lang="ts">
export default {
	streamsync: {
		name: "Column Container",
		description: "Serves as container for Column components",
		allowedChildrenTypes: ["column", "repeater", "separator"],
		category: "Layout",
		fields: {
			cssClasses
		},
	},
};
</script>

<script setup lang="ts">
import { inject } from "vue";
import injectionKeys from "../injectionKeys";
import { cssClasses } from "../renderer/sharedStyleFields";

const instanceData = inject(injectionKeys.instanceData);
instanceData.at(-1).value = { minimumNonCollapsiblePosition: undefined };
</script>

<style scoped>
@import "../renderer/sharedStyles.css";

.CoreColumns {
	width: 100%;
	max-width: 100%;
	flex-wrap: wrap;
	flex-direction: row;
}
</style>
