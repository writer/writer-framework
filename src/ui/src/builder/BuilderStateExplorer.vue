<template>
	<div class="BuilderStateExplorer">
		<SharedJsonViewer
			:data="wf.userState.value"
			:enable-copy-to-json="true"
			:initial-depth="1"
		></SharedJsonViewer>
	</div>
</template>

<script setup lang="ts">
import SharedJsonViewer from "@/components/shared/SharedJsonViewer/SharedJsonViewer.vue";

import injectionKeys from "@/injectionKeys";
import { inject } from "vue";

const wf = inject(injectionKeys.core);
</script>

<style scoped>
@import "./sharedStyles.css";

.BuilderStateExplorer {
	max-height: 70vh;
	overflow-y: auto;
}
</style>
