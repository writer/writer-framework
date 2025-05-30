<template>
	<div
		ref="rootEl"
		class="CoreTimer"
		:class="{ failing: isFailing }"
		:style="rootStyle"
	></div>
</template>

<script lang="ts">
import { FieldType } from "@/writerTypes";
import { validatorPositiveNumber } from "@/constants/validators";
import {
	accentColor,
	baseYesNoField,
	cssClasses,
} from "@/renderer/sharedStyleFields";
const description =
	"A component that emits an event repeatedly at specified time intervals, enabling time-based refresh.";

const ssTickHandlerStub = `
def handle_timer_tick(state):

	# Increment counter when the timer ticks

	state["counter"] += 1`.trim();

export default {
	writer: {
		name: "Timer",
		description,
		category: "Other",
		fields: {
			intervalMs: {
				name: "Interval (ms)",
				desc: "How much time to wait between ticks. A tick is considered finished when its event is handled.",
				default: "200",
				type: FieldType.Number,
				validator: validatorPositiveNumber,
			},
			isActive: {
				...baseYesNoField,
				name: "Active",
				default: "yes",
				desc: "Whether the timer should trigger tick events.",
			},
			accentColor,
			cssClasses,
		},
		events: {
			"wf-tick": {
				desc: "Emitted when the timer ticks.",
				stub: ssTickHandlerStub.trim(),
			},
		},
	},
};
</script>

<script setup lang="ts">
import {
	computed,
	inject,
	nextTick,
	onMounted,
	ref,
	useTemplateRef,
	watch,
} from "vue";
import injectionKeys from "@/injectionKeys";

const MIN_ANIMATION_RESET_MS = 500;
const MIN_ANIMATION_DURATION_MS = 1000;
const fields = inject(injectionKeys.evaluatedFields);
const wf = inject(injectionKeys.core);
const rootEl = useTemplateRef("rootEl");

const intervalMs = computed(() => fields.intervalMs.value);
const isActive = computed(() => fields.isActive.value);
const isFailing = ref(false);
const componentId = inject(injectionKeys.componentId);
const isTickHandlerSet = computed(
	() => !!wf.getComponentById(componentId)?.handlers?.["wf-tick"],
);

const rootStyle = computed(() => {
	const animationDurationMs = Math.max(
		intervalMs.value,
		MIN_ANIMATION_DURATION_MS,
	);
	return {
		"animation-duration": `${animationDurationMs}ms`,
	};
});

watch([isActive, intervalMs], () => {
	fireTimer();
});

watch(isTickHandlerSet, async (newIsTickHandlerSet) => {
	if (!newIsTickHandlerSet) return;
	await nextTick();
	fireTimer();
});

let animationTriggeredTime: number = 0;
let activeTimerId: ReturnType<typeof setTimeout> = null;

function clearActiveTimer() {
	clearTimeout(activeTimerId);
}

function fireTimer() {
	clearActiveTimer();

	if (!isActive.value || intervalMs.value < 0) return;
	if (!rootEl.value) return;

	if (Date.now() - animationTriggeredTime >= MIN_ANIMATION_RESET_MS) {
		rootEl.value.classList.remove("tick");
		rootEl.value.offsetWidth; // Forces a re-render
		animationTriggeredTime = Date.now();
		rootEl.value.classList.add("tick");
	}

	const callback = ({ ok }) => {
		isFailing.value = !ok;
		activeTimerId = setTimeout(() => {
			fireTimer();
		}, intervalMs.value);
	};
	const event = new CustomEvent("wf-tick", {
		detail: {
			callback,
		},
	});
	rootEl.value.dispatchEvent(event);
}
onMounted(() => {
	fireTimer();
});
</script>

<style scoped>
.CoreTimer {
	width: 12px;
	min-width: 12px;
	height: 12px;
	background: var(--accentColor);
	border-radius: 50%;
	filter: blur(1px);
}

.CoreTimer.failing {
	background: red;
}

.CoreTimer:not(.failing).tick {
	animation-name: tick;
}

@keyframes tick {
	0% {
		filter: blur(1px);
	}

	100% {
		filter: blur(3px);
	}
}
</style>
