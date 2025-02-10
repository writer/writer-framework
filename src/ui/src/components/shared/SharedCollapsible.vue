<template>
	<details
		class="SharedCollapsible"
		:class="{ 'SharedCollapsible--customMarker': icons }"
		:open="isOpen"
		:disabled="disabled"
		@toggle="onToggle"
	>
		<summary class="SharedCollapsible__summary">
			<span
				v-if="icons"
				class="SharedCollapsible__summary__icon material-symbols-outlined"
				>{{ icon }}</span
			>
			<slot name="title" />
		</summary>
		<div class="content">
			<slot name="content" />
		</div>
	</details>
</template>

<script setup lang="ts">
import { computed, PropType, ref, toRef, watch } from "vue";

const props = defineProps({
	open: { type: Boolean, required: false },
	disabled: { type: Boolean, required: false },
	icons: {
		type: Object as PropType<{ open: string; close: string }>,
		required: false,
		default: undefined,
	},
});

const emit = defineEmits({
	toggle: (open: boolean) => typeof open === "boolean",
});

const isOpen = ref(props.open);

watch(toRef(props, "open"), (value) => (isOpen.value = value));

const icon = computed(() => {
	if (props.icons === undefined) return undefined;
	return isOpen.value ? props.icons.open : props.icons.close;
});

function onToggle(event) {
	const state = event.newState === "open";
	isOpen.value = state;
	emit("toggle", state);
}
</script>

<style scoped>
/* customize the triangle and animate it */

details {
	box-sizing: border-box;
}

details summary::-webkit-details-marker {
	display: none;
}

details[open] > summary:before {
	transform: rotate(90deg);
}

summary {
	outline: none;
	display: flex;
	padding-left: 16px;
	position: relative;
	cursor: pointer;
}

details summary:before {
	content: "";
	border-width: 6px;
	border-style: solid;
	border-color: transparent transparent transparent var(--accentColor);
	position: absolute;
	left: 4px;
	top: 2px;

	transform: rotate(0);
	transform-origin: 3px 50%;
	transition: 0.3s transform ease;
}

.SharedCollapsible--customMarker summary {
	padding-left: unset;
	display: grid;
	grid-template-columns: auto 1fr;
	gap: 6px;
	align-items: center;
}
.SharedCollapsible--customMarker summary:before {
	content: none;
}
.SharedCollapsible__summary__icon {
	height: 18px;
	width: 18px;
	display: flex;
	align-items: center;
	justify-content: center;
}

summary:focus-visible:before {
	border-color: transparent transparent transparent var(--primaryTextColor);
}

@media (prefers-reduced-motion) {
	summary:before {
		transition: unset;
	}
}

/* small animation on the content */

details[open] summary ~ .content {
	animation: sweep 0.2s ease-in-out;
}

@media (prefers-reduced-motion) {
	details[open] summary ~ .content {
		animation: unset;
	}
}

@keyframes sweep {
	0% {
		opacity: 0;
		margin-top: -12px;
	}
	100% {
		opacity: 1;
		margin-top: 0;
	}
}
</style>
