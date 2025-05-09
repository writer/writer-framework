<template>
	<BuilderComment v-if="shouldDiplay" :component-id="componentId" />
</template>

<script lang="ts">
import BuilderComment from "@/builder/comment/BuilderComment.vue";

const description = "TODO";

export default {
	writer: {
		name: "Comment",
		description,
		category: "Other",
		fields: {},
	},
};
</script>
<script setup lang="ts">
import { computed, inject } from "vue";
import injectionKeys from "@/injectionKeys";

const wf = inject(injectionKeys.core);
const wfbm = inject(injectionKeys.builderManager);
const componentId = inject(injectionKeys.componentId);

const shouldDiplay = computed(
	() => wf.mode.value === "edit" && wfbm.mode.value !== "preview",
);
</script>

<style scoped>
@import "@/renderer/sharedStyles.css";
@import "@/renderer/colorTransformations.css";

.CoreComment {
	position: absolute;
}
</style>
