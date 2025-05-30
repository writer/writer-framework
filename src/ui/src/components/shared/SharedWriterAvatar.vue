<script setup lang="ts">
import { useWriterApiUserProfile } from "@/composables/useWriterApiUser";
import WdsSkeletonLoader from "@/wds/WdsSkeletonLoader.vue";
import { computed, ref } from "vue";

const props = defineProps({
	userId: { type: Number, required: true },
	showTooltip: { type: Boolean, required: false },
});

const userId = computed(() => props.userId);

const imgLoaded = ref(false);

const { user, isLoading } = useWriterApiUserProfile(userId);

const avatarUrl = computed(() => user.value?.avatar ?? "");
const initials = computed(() => {
	return (user.value?.firstName ?? "?").at(0);
});
const tooltip = computed(() => {
	if (!props.showTooltip || !user.value) return undefined;
	return `${user.value.firstName ?? ""} ${user.value.lastName ?? ""}`;
});

const imgAlt = computed(() => {
	if (!user.value) return `Avatar of the user ID ${userId.value}`;
	return `Avatar of ${user.value.firstName ?? ""} ${user.value.lastName ?? ""}`;
});
</script>

<template>
	<div class="SharedWriterAvatar" :data-writer-tooltip="tooltip">
		<WdsSkeletonLoader
			v-if="isLoading || (avatarUrl && !imgLoaded)"
			class="SharedWriterAvatar__loader"
		/>

		<template v-if="!isLoading">
			<img
				v-if="!!avatarUrl"
				v-show="imgLoaded"
				:src="avatarUrl"
				:alt="imgAlt"
				class="SharedWriterAvatar__img"
				@load="imgLoaded = true"
			/>
			<div v-else class="SharedWriterAvatar__initials">
				{{ initials }}
			</div>
		</template>
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
