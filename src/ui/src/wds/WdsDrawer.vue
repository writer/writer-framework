<template>
	<Teleport to="#drawer">
		<Transition name="drawer">
			<div v-if="isOpen" class="WdsDrawer__overlay" @click="close">
				<div
					class="WdsDrawer__container"
					:class="`WdsDrawer__container--${size}`"
					@click.stop
				>
					<div class="WdsDrawer__header">
						<slot name="header">
							<h2 class="WdsDrawer__header__title">
								{{ title }}
							</h2>
						</slot>
						<WdsButton variant="neutral" size="icon" @click="close">
							<WdsIcon name="x" />
						</WdsButton>
					</div>
					<div class="WdsDrawer__content">
						<slot />
					</div>
				</div>
			</div>
		</Transition>
	</Teleport>
</template>

<script setup lang="ts">
import { PropType } from "vue";
import WdsButton from "./WdsButton.vue";
import WdsIcon from "./WdsIcon.vue";

defineProps({
	title: { type: String, default: "" },
	size: {
		type: String as PropType<"small" | "medium" | "large">,
		default: "medium",
	},
});

const isOpen = defineModel<boolean>("modelValue", { required: true });
function close() {
	isOpen.value = false;
}
</script>

<style scoped>
.WdsDrawer__overlay {
	position: fixed;
	top: 0;
	left: 0;
	right: 0;
	bottom: 0;
	background: rgba(0, 0, 0, 0.5);
	z-index: 10;
	display: flex;
	justify-content: flex-end;
}

.WdsDrawer__container {
	background: var(--wdsColorWhite);
	height: 100%;
	display: flex;
	flex-direction: column;
	box-shadow: var(--wdsShadowLarge);
}

.WdsDrawer__container--small {
	width: 400px;
}

.WdsDrawer__container--medium {
	width: 600px;
}

.WdsDrawer__container--large {
	width: 800px;
}

.WdsDrawer__header {
	display: flex;
	justify-content: space-between;
	align-items: center;
	padding: 20px;
	border-bottom: 1px solid var(--wdsColorGray2);
	flex-shrink: 0;
}

.WdsDrawer__header__title {
	margin: 0;
	font-size: 20px;
	font-weight: 600;
	color: var(--wdsColorBlack);
}

.WdsDrawer__content {
	flex: 1;
	overflow-y: auto;
	padding: 0;
}

.drawer-enter-active,
.drawer-leave-active {
	transition: opacity 0.3s ease;
}

.drawer-enter-active .WdsDrawer__container,
.drawer-leave-active .WdsDrawer__container {
	transition: transform 0.3s ease;
}

.drawer-enter-from,
.drawer-leave-to {
	opacity: 0;
}

.drawer-enter-from .WdsDrawer__container {
	transform: translateX(100%);
}

.drawer-leave-to .WdsDrawer__container {
	transform: translateX(100%);
}
</style>
