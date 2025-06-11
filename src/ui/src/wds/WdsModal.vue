<!-- eslint-disable @typescript-eslint/ban-types -->
<template>
	<Teleport to="#modal">
		<div
			class="WdsModal colorTransformer"
			:class="{
				'WdsModal--overflow': allowOverflow,
				'WdsModal--wide': size == 'wide',
			}"
			tabindex="-1"
		>
			<div class="WdsModal__main">
				<WdsButton
					v-if="displayCloseButton"
					variant="neutral"
					size="smallIcon"
					class="WdsModal__main__closeBtn"
					@click="$emit('close')"
				>
					<i class="material-symbols-outlined">close</i>
				</WdsButton>
				<div v-if="title || description" class="WdsModal__main__title">
					<div class="WdsModal__main__title__header">
						<h2>{{ title }}</h2>
						<slot name="titleActions" />
					</div>
					<summary v-if="description">
						{{ description }}
					</summary>
				</div>
				<div class="WdsModal__main__content"><slot></slot></div>
				<div
					v-if="actions?.length > 0 || hint"
					class="WdsModal__main__footer"
				>
					<p v-if="hint" class="WdsModal__main__footer__hint">
						{{ hint }}
					</p>
					<div
						v-if="actions?.length > 0"
						class="WdsModal__main__footer__actions"
					>
						<WdsButton
							v-for="(action, index) in actions"
							:key="index"
							:variant="
								index == actions.length - 1
									? 'primary'
									: 'tertiary'
							"
							:disabled="action.disabled"
							@click="action.fn"
						>
							<i
								v-if="action.icon"
								class="material-symbols-outlined"
								>{{ action.icon }}</i
							>
							{{ action.desc }}
						</WdsButton>
					</div>
				</div>
			</div>
		</div>
	</Teleport>
</template>

<script setup lang="ts">
import WdsButton from "@/wds/WdsButton.vue";
import { PropType, toRefs } from "vue";

export type ModalAction = {
	desc: string;
	fn: (..._args: unknown[]) => unknown;
	disabled?: boolean;
	icon?: string;
};

const props = defineProps({
	title: { type: String, required: false, default: null },
	size: {
		type: String as PropType<"normal" | "wide">,
		required: false,
		default: "normal",
	},
	description: { type: String, required: false, default: null },
	actions: {
		type: Array as PropType<ModalAction[]>,
		required: false,
		default: () => [],
	},
	allowOverflow: { type: Boolean, required: false },
	displayCloseButton: { type: Boolean, required: false },
	hint: { type: String, required: false, default: undefined },
});

defineEmits({
	close: () => true,
});

const { title, actions } = toRefs(props);
</script>

<style scoped>
@import "@/renderer/colorTransformations.css";

.WdsModal {
	background: rgba(0, 0, 0, 0.1);
	width: 100vw;
	height: 100vh;
	display: flex;
	align-items: center;
	justify-content: center;
}

.WdsModal__main {
	padding: 32px;
	background: var(--wdsColorWhite);
	width: 80%;
	overflow: hidden;
	max-width: 120ch;
	border-radius: 8px;
	border: 1px solid var(--separatorColor);
	box-shadow: 0px 3px 40px 0px rgba(172, 185, 220, 0.4);
	position: relative;
}

.WdsModal--wide .WdsModal__main {
	max-width: 240ch;
}

.WdsModal--overflow .WdsModal__main,
.WdsModal--overflow .WdsModal__main__content {
	overflow: unset;
}

.WdsModal__main__closeBtn {
	position: absolute;
	right: 8px;
	top: 8px;
}

.WdsModal__main__footer {
	margin-top: 32px;
	display: flex;
	align-items: center;
}
.WdsModal__main__footer__hint {
	color: var(--wdsColorGray5);
	font-size: 12px;
	flex-grow: 1;
}
.WdsModal__main__footer__actions {
	display: flex;
	justify-content: right;
	gap: 8px;
}
/* let action take full width to right align if hint is not present */
.WdsModal__main__footer:has(:not(.WdsModal__main__footer__hint))
	.WdsModal__main__footer__actions {
	flex-grow: 1;
}

.WdsModal__main__title {
	margin-bottom: 32px;
}

/* center the actions slot if the slot is provided */
.WdsModal__main__title__header {
	display: grid;
	grid-template-columns: 1fr auto 1fr;
}
.WdsModal__main__title__header > *:only-child {
	grid-column: 1 / -1;
}

.WdsModal__main__title__header h2 {
	margin: 0;
	font-size: 24px;
	font-style: normal;
	font-weight: 500;
	line-height: 160%;
}

.WdsModal__main__title summary {
	color: var(--secondaryTextColor);
	font-size: 14px;
	margin-top: 4px;
	line-height: 180%;
}

.WdsModal__main__content {
	max-height: 60vh;
	overflow-x: hidden;
	overflow-y: auto;
}
.WdsModal--overflow .slotContainer {
	overflow: unset;
}
</style>
