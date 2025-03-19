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
			<div class="main">
				<div v-if="title || description" class="titleContainer">
					<h2>{{ title }}</h2>
					<summary v-if="description">
						{{ description }}
					</summary>
				</div>
				<div class="slotContainer"><slot></slot></div>
				<div v-if="actions?.length > 0" class="actionContainer">
					<WdsButton
						v-for="(action, index) in actions"
						:key="index"
						:variant="
							index == actions.length - 1 ? 'primary' : 'tertiary'
						"
						@click="action.fn"
					>
						{{ action.desc }}
					</WdsButton>
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
		required: true,
		default: undefined,
	},
	allowOverflow: { type: Boolean, required: false },
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

.main {
	padding: 32px;
	background: var(--wdsColorWhite);
	width: 80%;
	overflow: hidden;
	max-width: 120ch;
	border-radius: 8px;
	border: 1px solid var(--separatorColor);
	box-shadow: 0px 3px 40px 0px rgba(172, 185, 220, 0.4);
}

.WdsModal--wide .main {
	max-width: 240ch;
}

.WdsModal--overflow .main {
	overflow-y: unset;
}

h2 {
	margin: 0;
	font-size: 24px;
	font-style: normal;
	font-weight: 500;
	line-height: 160%;
}

summary {
	color: var(--secondaryTextColor);
	font-size: 14px;
	margin-top: 4px;
	line-height: 180%;
}

.titleContainer {
	margin-bottom: 32px;
}

.slotContainer {
	max-height: 60vh;
	overflow-x: hidden;
	overflow-y: auto;
}
.WdsModal--overflow .slotContainer {
	overflow: unset;
}

.actionContainer {
	display: flex;
	justify-content: right;
	margin-top: 32px;
	gap: 8px;
}
</style>
