<script setup lang="ts">
import { useWriterApiUserProfile } from "@/composables/useWriterApiUser";
import WdsSkeletonLoader from "@/wds/WdsSkeletonLoader.vue";
import { computed } from "vue";

const props = defineProps({
	userId: { type: Number, required: true },
});

const userId = computed(() => props.userId);

const { user, isLoading } = useWriterApiUserProfile(userId);

const avatarUrl = computed(() => user.value?.avatar ?? "");
const initials = computed(() => {
	return (user.value?.firstName ?? "?").at(0);
});
</script>

<template>
	<WdsSkeletonLoader v-if="isLoading" class="SharedWriterAvatar--loader" />
	<img
		v-else-if="avatarUrl"
		:src="avatarUrl"
		class="SharedWriterAvatar--img"
	/>
	<div v-else class="SharedWriterAvatar--initials">
		{{ initials }}
	</div>
</template>

<style lang="css" scoped>
.SharedWriterAvatar--img,
.SharedWriterAvatar--initials,
.SharedWriterAvatar--loader {
	border-radius: 50%;
	width: var(--sharedWriterAvatarSize, 32px);
	height: var(--sharedWriterAvatarSize, 32px);
}

.SharedWriterAvatar--initials {
	display: flex;
	background-color: var(--wdsColorPurple3);
	color: var(--wdsColorBlack);
	font-size: 12px;
	align-items: center;
	justify-content: center;
}
</style>
