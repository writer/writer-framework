<template>
	<div class="CoreChatbotMessage" :aria-busy="isLoading">
		<CoreChatbotAvatar :initials="initials" />
		<div
			class="CoreChatbotMessage__content"
			:style="{ background: contentBgColor }"
		>
			<WdsLoaderDots v-if="displayLoader" />
			<div v-else class="CoreChatbotMessage__content__text">
				<BaseMarkdown v-if="useMarkdown" :raw-text="content">
				</BaseMarkdown>
				<template v-else>
					{{ content }}
				</template>
			</div>
			<div
				v-if="actions.length"
				class="CoreChatbotMessage__content__actions"
			>
				<button
					v-for="(action, actionIndex) in actions"
					:key="actionIndex"
					class="action"
					@click="$emit('actionClick', action)"
				>
					<div v-if="action.subheading" class="subheading">
						{{ action.subheading }}
					</div>
					<h3 class="name">{{ action.name }}</h3>
					<div v-if="action.desc" class="desc">
						{{ action.desc }}
					</div>
				</button>
			</div>
		</div>
	</div>
</template>

<script lang="ts">
export type Action = {
	subheading?: string;
	name: string;
	desc?: string;
	data?: string;
};

export type Message = {
	role: string;
	pending: boolean;
	content: string;
	actions?: Action[];
};
</script>

<script lang="ts" setup>
import { computed, defineAsyncComponent, PropType } from "vue";
import CoreChatbotAvatar from "./CoreChatbotAvatar.vue";

const BaseMarkdown = defineAsyncComponent(
	() => import("../../base/BaseMarkdown.vue"),
);
const WdsLoaderDots = defineAsyncComponent(
	() => import("@/wds/WdsLoaderDots.vue"),
);

const props = defineProps({
	initials: { type: String, required: true },
	useMarkdown: { type: Boolean, required: false },
	message: {
		type: Object as PropType<Message>,
		required: false,
		default: undefined,
	},
	assistantRoleColor: { type: String, required: false, default: "" },
	isLoading: { type: Boolean, required: false },
});

defineEmits({
	actionClick: (action: Action) =>
		typeof action === "object" && action !== null,
});

const actions = computed<Action[]>(() => props.message?.actions ?? []);

const displayLoader = computed(() => {
	return props.isLoading && !content.value;
});

const role = computed(() => {
	if (props.isLoading) return "assistant";
	return props.message?.role ?? "";
});

const content = computed(() => props.message?.content.trim() ?? "");

const contentBgColor = computed(() => {
	switch (role.value) {
		case "user":
			return "var(--userRoleColor)";
		case "assistant":
			return (
				props.assistantRoleColor ||
				"linear-gradient(264deg, #f5ebff 0.71%, #eef1ff 100%)"
			);
		default:
			return "";
	}
});
</script>

<style scoped>
.CoreChatbotMessage {
	display: flex;
	gap: 8px;
}

.CoreChatbotMessage__content {
	border-radius: 8px;
	width: fit-content;
	flex: 0 1 auto;
	color: var(--primaryTextColor);
}

.CoreChatbotMessage__content__text {
	line-height: 2;
	padding: 12px 16px 12px 16px;
}

.CoreChatbotMessage__content__actions {
	padding: 16px;
	background: rgba(0, 0, 0, 0.02);
	display: flex;
	gap: 12px;
	flex-wrap: wrap;
}

.CoreChatbotMessage__content__actions .action {
	padding: 12px;
	border-radius: 4px;
	background: var(--containerBackgroundColor);
	overflow: hidden;
	line-height: normal;
	display: flex;
	gap: 4px;
	flex-direction: column;
	box-shadow: 0 2px 2px 0px rgba(0, 0, 0, 0.1);
	cursor: pointer;
	border: 0;
}

.action .subheading {
	color: var(--secondaryTextColor);
	font-size: 0.7rem;
}

.action .desc {
	font-size: 0.7rem;
}
</style>
