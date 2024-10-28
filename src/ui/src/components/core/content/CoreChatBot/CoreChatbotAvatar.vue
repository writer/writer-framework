<template>
	<div class="CoreChatbotAvatar">{{ initials }}</div>
</template>

<script lang="ts" setup>
defineProps({
	initials: { type: String, required: true },
});
</script>

<style scoped>
.CoreChatbotAvatar {
	border-radius: 50%;
	background: var(--avatarBackgroundColor);
	color: var(--avatarTextColor);
	margin-top: 6px;
	height: 32px;
	width: 32px;
	flex: 0 0 32px;
	display: flex;
	font-weight: 500;
	font-size: 0.75rem;
	align-items: center;
	justify-content: center;
	overflow: hidden;
	text-transform: uppercase;
}
</style>
