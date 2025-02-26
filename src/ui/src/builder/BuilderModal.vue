<!-- eslint-disable @typescript-eslint/ban-types -->
<template>
	<Teleport to="#modal">
		<div
			class="BuilderModal"
			:class="{ 'BuilderModal--overflow': allowOverflow }"
			tabindex="-1"
			@keydown="handleKeydown"
		>
			<div class="main">
				<div class="titleContainer">
					<i v-if="icon" class="material-symbols-outlined">{{
						icon
					}}</i>
					<h2>{{ modalTitle }}</h2>
					<WdsButton
						variant="neutral"
						size="icon"
						:data-writer-tooltip="closeAction?.desc ?? 'Close'"
						@click="closeAction.fn"
					>
						<i class="material-symbols-outlined">close</i>
					</WdsButton>
				</div>
				<div class="slotContainer">
					<slot></slot>
				</div>
				<div v-if="menuActions?.length > 0" class="actionContainer">
					<WdsButton
						v-for="(action, index) in menuActions"
						:key="index"
						variant="primary"
						size="small"
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
	modalTitle: { type: String, required: true },
	icon: { type: String, required: false, default: undefined },
	closeAction: { type: Object as PropType<ModalAction>, required: true },
	menuActions: {
		type: Array as PropType<ModalAction[]>,
		required: false,
		default: undefined,
	},
	allowOverflow: { type: Boolean, required: false },
});

const { modalTitle, icon, closeAction, menuActions } = toRefs(props);

const handleKeydown = (ev: KeyboardEvent) => {
	if (ev.key == "Escape") {
		closeAction.value.fn();
	}
};
</script>

<style scoped>
@import "./sharedStyles.css";

.BuilderModal {
	background: rgba(0, 0, 0, 0.1);
	width: 100vw;
	height: 100vh;
	display: flex;
	align-items: center;
	justify-content: center;
}

.main {
	background: white;
	width: 80%;
	overflow: hidden;
	max-width: 120ch;
	border-radius: 12px;
	box-shadow: 0px 3px 40px 0px rgba(172, 185, 220, 0.4);
}

.BuilderModal--overflow .main {
	overflow: unset;
}

.titleContainer {
	border-bottom: 1px solid var(--builderSubtleSeparatorColor);
	padding: 8px 8px 8px 16px;
	gap: 12px;
	display: flex;
	align-items: center;
	font-size: 1rem;
}

.titleContainer button {
	margin-left: auto;
}

.slotContainer {
	padding: 16px;
	max-height: 60vh;
	overflow: auto;
}
.BuilderModal--overflow .slotContainer {
	overflow: unset;
}

.actionContainer {
	border-top: 1px solid var(--builderSubtleSeparatorColor);
	padding: 16px;
}
</style>
