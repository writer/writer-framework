<template>
	<div ref="rootEl" class="BuilderCollaborationTracker">
		{{ connectedProfilesByComponent }}
	</div>
</template>
<script setup lang="ts">
import { connectedProfilesByComponent } from "@/composables/useCollaboration";
</script>

<style scoped>
.BuilderCollaborationTracker {
}
</style>
