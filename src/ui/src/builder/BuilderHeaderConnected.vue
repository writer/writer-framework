<template>
	<div
		v-if="connectedCount > 0"
		class="BuilderHeaderConnected"
		:data-writer-tooltip="tooltip"
		data-writer-tooltip-placement="bottom"
	>
		<div v-if="connectedCount == 1" class="profile">
			{{ initialFirstUser }}
		</div>
		<div v-if="connectedCount > 1" class="profile">
			+{{ connectedCount }}
		</div>
	</div>
</template>

<script setup lang="ts">
import { connectedProfiles } from "@/composables/useCollaboration";
import { computed } from "vue";

const connectedCount = computed(() => connectedProfiles.value.length);
const initialFirstUser = computed(() => {
	const name = connectedProfiles.value?.[0].displayName;
	if (name == "Unknown") return "?";
	return name.charAt(0);
});

const tooltip = computed(() => {
	const message =
		"Also editing: " +
		connectedProfiles.value
			.map((profile) => profile.displayName)
			.join(", ");
	return message;
});
</script>

<style scoped>

.BuilderHeaderConnected {
}

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

.profile .avatar {
	width: 32px;
	height: 32px;
	position: absolute;
	top: 0;
	left: 0;
	background-size: 32px 32px;
	background-repeat: no-repeat;
	background-position: center;
}

</style>
