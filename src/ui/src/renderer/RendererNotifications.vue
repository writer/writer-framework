<template>
	<div
		v-show="notifications.length > 0"
		class="RendererNotifications colorTransformer"
		@click="toggle"
	>
		<div ref="balloon" class="balloon" title="Toggle notifications">
			<i class="icon material-symbols-outlined"> notifications </i>
			<div class="counter">{{ notifications.length }}</div>
		</div>
		<div class="balloonFlash"></div>
		<div v-show="isActive" class="main">
			<div class="clearContainer">
				<WdsButton @click="clearAll">
					<i class="material-symbols-outlined"> clear_all </i>
					Clear all
				</WdsButton>
			</div>
			<div
				v-for="(notification, notificationId) in notifications"
				:key="notificationId"
				class="notification"
			>
				<div class="icon" :class="notification.type">
					<i class="material-symbols-outlined"> exclamation </i>
				</div>
				<div class="content">
					<header>
						<strong class="title">{{ notification.title }}</strong>
						<span class="time">{{
							notification.timestampReceived.toLocaleTimeString()
						}}</span>
					</header>
					<div class="message">{{ notification.message }}</div>
				</div>
			</div>
		</div>
	</div>
</template>

<script setup lang="ts">
import { inject, onMounted, reactive, ref, useTemplateRef } from "vue";
import injectionKeys from "@/injectionKeys";
import WdsButton from "@/wds/WdsButton.vue";

const MAX_ITEMS_IN_LIST = 100;
const wf = inject(injectionKeys.core);
const isActive = ref(false);
const balloon = useTemplateRef("balloon");

const notifications: {
	type: string;
	title: string;
	message: string;
	code: string;
	timestampReceived: Date;
}[] = reactive([]);

const handleNotification = (notification: {
	type: string;
	title: string;
	message: string;
	code?: string;
}) => {
	const { type, title, message, code } = notification;
	notifications.unshift({
		type,
		title,
		message,
		code,
		timestampReceived: new Date(),
	});
	notifications.splice(MAX_ITEMS_IN_LIST);
	balloon.value.classList.remove("alert");
	balloon.value.offsetWidth; // Forces a re-render
	balloon.value.classList.add("alert");
};

onMounted(() => {
	wf.addMailSubscription("notification", handleNotification);
});

const toggle = () => {
	if (notifications.length == 0) return;
	isActive.value = !isActive.value;
};

const clearAll = () => {
	notifications.splice(0);
	isActive.value = false;
};
</script>

<style scoped>
@import "./sharedStyles.css";
@import "./colorTransformations.css";

.RendererNotifications {
	position: sticky;
	top: 24px;
	margin-left: auto;
	margin-right: 24px;
	max-width: 70ch;
	width: 40vw;
	z-index: 3;
	--buttonColor: var(--wdsColorBlue5);
}

.balloonFlash {
	right: 0;
	position: absolute;
	opacity: 0.8;
	background: var(--accentColor);
	width: 52px;
	height: 52px;
	border-radius: 50%;
}

.balloon.alert + .balloonFlash {
	animation-name: alert;
	animation-duration: 1s;
	animation-timing-function: ease-in-out;
}

.balloon {
	z-index: 2;
	position: absolute;
	user-select: none;
	right: 0;
	font-size: 0.7rem;
	border-radius: 50%;
	background: var(--accentColor);
	width: 52px;
	height: 52px;
	color: var(--emptinessColor);
	display: flex;
	align-items: center;
	justify-content: center;
	cursor: pointer;
	box-shadow: 0 0 8px 2px rgba(0, 0, 0, 0.2);
	flex-direction: column;
}

.balloon .icon {
	font-size: 1.25rem;
}

.balloon.alert .icon {
	animation-name: ring;
	animation-duration: 0.3s;
	animation-iteration-count: 4;
	animation-timing-function: ease-in-out;
}

.balloon .counter {
	position: absolute;
	top: 40px;
	right: 0px;
	background: var(--containerBackgroundColor);
	padding: 4px 8px 4px 8px;
	border-radius: 16px;
	color: var(--primaryTextColor);
	border: 1px solid var(--separatorColor);
}

@keyframes alert {
	0% {
		transform: scale(1);
	}
	50% {
		transform: scale(1.7);
	}
	100% {
		transform: scale(1);
	}
}

@keyframes ring {
	0% {
		transform: rotate(0deg);
	}
	25% {
		transform: rotate(-25deg);
	}
	75% {
		transform: rotate(25deg);
	}
	100% {
		transform: rotate(0deg);
	}
}

.main {
	position: absolute;
	max-height: 75vh;
	overflow-y: auto;
	overflow-x: hidden;
	right: 0;
	width: 100%;
	max-width: 100%;
	top: calc(48px + 24px);
	color: var(--primaryTextColor);
	background: var(--containerBackgroundColor);
	border-radius: 8px;
	box-shadow: 0 0 8px 0px rgba(0, 0, 0, 0.2);
}

.clearContainer {
	padding: 16px;
}

.clearContainer button {
	margin-left: auto;
	margin-right: 0;
}

.notification {
	border-top: 1px solid var(--separatorColor);
	padding: 16px 16px 16px 0;
	font-size: 0.8rem;
	display: grid;
	grid-template-rows: 1fr;
	grid-template-columns: 72px 1fr;
	align-items: center;
}

.notification .icon {
	grid-area: 1/1;
	text-align: center;
	font-size: 1.25rem;
}

.notification .icon.error {
	color: #fb0000;
}
.notification .icon.warning {
	color: #fb9600;
}
.notification .icon.info {
	color: #00adb8;
}
.notification .icon.success {
	color: #00b800;
}

.notification .content {
	grid-area: 1/2;
	max-width: 100%;
	overflow: hidden;
}

.notification header {
	display: flex;
}

.notification header .title {
	flex: 1 0 auto;
}

.notification header .time {
	flex: 0 0 auto;
	color: var(--secondaryTextColor);
}

.message {
	margin-top: 4px;
}
</style>
