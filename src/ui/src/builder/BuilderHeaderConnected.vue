<template>
	<div
		v-if="connectedCount > 0"
		class="BuilderHeaderConnected"
		:data-writer-tooltip="tooltip"
		data-writer-tooltip-placement="bottom"
	>
		<div v-if="connectedCount == 1" class="profile">
			<SharedWriterAvatar
				:user-id="firstUser.userId"
			></SharedWriterAvatar>
		</div>
		<div v-if="connectedCount > 1" class="profile">
			+{{ connectedCount }}
		</div>
	</div>
</template>

<script setup lang="ts">
import SharedWriterAvatar from "@/components/shared/SharedWriterAvatar.vue";
import injectionKeys from "@/injectionKeys";
import { computed, inject } from "vue";
const collaborationManager = inject(injectionKeys.collaborationManager);

const connectedCount = computed(
	() => collaborationManager.connectedProfiles.value.length,
);

const firstUser = computed(() => {
	return collaborationManager.connectedProfiles.value?.[0];
});

const tooltip = computed(() => {
	const message =
		"Also editing: " +
		collaborationManager.connectedProfiles.value
			.map((profile) => profile.displayName)
			.join(", ");
	return message;
});
</script>

<style scoped>
.profile {
	width: 32px;
	height: 32px;
	background: #e1a0ff;
	color: #000000;
	border-radius: 50%;
	display: flex;
	align-items: center;
	justify-content: center;
	overflow: hidden;
	position: relative;
}
</style>
