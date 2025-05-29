<script setup lang="ts">
import { useWriterApiUserProfile } from "@/composables/useWriterApiUser";
import WdsSkeletonLoader from "@/wds/WdsSkeletonLoader.vue";
import { computed, ref } from "vue";

const props = defineProps({
	userId: { type: Number, required: true },
});

const userId = computed(() => props.userId);

const imgLoaded = ref(false);

const { user, isLoading } = useWriterApiUserProfile(userId);

const avatarUrl = computed(() => user.value?.avatar ?? "");
const initials = computed(() => {
	return (user.value?.firstName ?? "?").at(0);
});
</script>

<template>
	<div class="SharedWriterAvatar">
		<WdsSkeletonLoader
			v-if="isLoading || (avatarUrl && !imgLoaded)"
			class="SharedWriterAvatar__loader"
		/>

		<img
			v-if="!!avatarUrl"
			v-show="imgLoaded"
			:src="avatarUrl"
			class="SharedWriterAvatar__img"
			@load="imgLoaded = true"
		/>
		<div v-else class="SharedWriterAvatar__initials">
			{{ initials }}
		</div>
	</div>
</template>

<style lang="css" scoped>
.SharedWriterAvatar {
	border-radius: 50%;
	width: var(--sharedWriterAvatarSize, 32px);
	height: var(--sharedWriterAvatarSize, 32px);
}
.SharedWriterAvatar__img,
.SharedWriterAvatar__initials,
.SharedWriterAvatar__loader {
	border-radius: 50%;
	width: 100%;
	height: 100%;
}

.SharedWriterAvatar__initials {
	display: flex;
	background-color: var(--wdsColorPurple3);
	color: var(--wdsColorBlack);
	font-size: 12px;
	align-items: center;
	justify-content: center;
}
</style>
