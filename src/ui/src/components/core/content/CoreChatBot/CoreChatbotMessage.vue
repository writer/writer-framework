<template>
	<div class="CoreChatbotMessage" :aria-busy="isLoading">
		<CoreChatbotAvatar :initials="initials" />
		<div
			class="CoreChatbotMessage__content"
			:style="{ background: contentBgColor }"
		>
			<WdsLoaderDots v-if="displayLoader" />
			<div v-else class="CoreChatbotMessage__content__text">
				<!-- Handle multimodal content (array) -->
				<template v-if="Array.isArray(content)">
					<!-- Render text fragments first -->
					<template
						v-for="(fragment, index) in content"
						:key="`text-${index}`"
					>
						<div
							v-if="fragment.type === 'text'"
							class="content-fragment"
						>
							<BaseMarkdown
								v-if="useMarkdown"
								:raw-text="fragment.text || ''"
							>
							</BaseMarkdown>
							<span v-else>{{ fragment.text }}</span>
						</div>
					</template>

					<!-- Render images in horizontal scrollable container -->
					<div
						v-if="hasImages(content)"
						class="message-images-wrapper"
					>
						<div class="message-images-container">
							<template
								v-for="(fragment, index) in content"
								:key="`image-${index}`"
							>
								<img
									v-if="
										fragment.type === 'image_url' &&
										fragment.image_url?.url
									"
									:src="fragment.image_url?.url"
									:alt="'Image from conversation'"
									class="message-image-preview"
									loading="lazy"
									role="button"
									tabindex="0"
									:aria-label="`Open image in modal - ${fragment.image_url?.url}`"
									@error="handleImageError"
									@click="
										modalImageUrl = fragment.image_url.url
									"
									@keydown="
										handleImageKeydown(
											$event,
											fragment.image_url.url,
										)
									"
								/>
							</template>
						</div>
					</div>
				</template>
				<!-- Handle string content -->
				<template v-else>
					<BaseMarkdown v-if="useMarkdown" :raw-text="content">
					</BaseMarkdown>
					<template v-else>
						{{ content }}
					</template>
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

	<!-- Image Modal -->
	<WdsModal
		v-if="modalImageUrl"
		:display-close-button="true"
		@close="modalImageUrl = undefined"
	>
		<img
			:src="modalImageUrl"
			alt="Full size image"
			class="image-modal-img"
		/>
	</WdsModal>
</template>

<script lang="ts">
export type Action = {
	subheading?: string;
	name: string;
	desc?: string;
	data?: string;
};

export type ContentFragment = {
	type: "text" | "image_url";
	text?: string;
	image_url?: { url: string };
};

export type Message = {
	role: string;
	pending: boolean;
	content: string | ContentFragment[];
	actions?: Action[];
};
</script>

<script lang="ts" setup>
import { computed, PropType, ref } from "vue";
import CoreChatbotAvatar from "./CoreChatbotAvatar.vue";
import WdsModal from "@/wds/WdsModal.vue";
import { defineAsyncComponentWithLoader } from "@/utils/defineAsyncComponentWithLoader";

const BaseMarkdown = defineAsyncComponentWithLoader({
	loader: () => import("../../base/BaseMarkdown.vue"),
});
const WdsLoaderDots = defineAsyncComponentWithLoader({
	loader: () => import("@/wds/WdsLoaderDots.vue"),
});

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

const content = computed(() => {
	const rawContent = props.message?.content;
	if (Array.isArray(rawContent)) {
		// For multimodal content, we'll handle rendering in the template
		return rawContent;
	}
	// For string content, trim as before
	return rawContent?.trim() ?? "";
});

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

const handleImageError = (event: Event) => {
	const img = event.target as HTMLImageElement;
	img.style.display = "none";
};

const modalImageUrl = ref<string | undefined>();

const hasImages = (content: ContentFragment[]) => {
	return content.some(
		(fragment) => fragment.type === "image_url" && fragment.image_url?.url,
	);
};

const handleImageKeydown = (event: KeyboardEvent, imageUrl: string) => {
	if (event.key === "Enter" || event.key === " ") {
		event.preventDefault();
		modalImageUrl.value = imageUrl;
	}
};
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

.CoreChatbotMessage__content__text :deep(h1),
.CoreChatbotMessage__content__text :deep(h2),
.CoreChatbotMessage__content__text :deep(h3) {
	margin-bottom: 8px !important;
}

.CoreChatbotMessage__content__actions {
	padding: 16px;
	background: var(--wdsColorBackground);
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
	box-shadow: var(--wdsShadowSm);
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

.content-fragment {
	margin-bottom: 8px;
}

.content-fragment:last-child {
	margin-bottom: 0;
}

.message-images-wrapper {
	max-width: 400px; /* 25rem equivalent at 16px base */
	margin-top: 8px;
}

.message-images-container {
	display: flex;
	gap: 8px;
	overflow-x: auto;
	overflow-y: hidden;
	padding: 4px 0;
	scrollbar-width: thin;
}

.message-images-container::-webkit-scrollbar {
	height: 4px;
}

.message-images-container::-webkit-scrollbar-track {
	background: var(--wdsColorGray1);
	border-radius: 2px;
}

.message-images-container::-webkit-scrollbar-thumb {
	background: var(--wdsColorGray4);
	border-radius: 2px;
}

.message-images-container::-webkit-scrollbar-thumb:hover {
	background: var(--wdsColorGray5);
}

.message-image-preview {
	width: 120px;
	height: 80px;
	object-fit: cover;
	border-radius: 8px;
	box-shadow: var(--wdsShadowMd);
	flex-shrink: 0;
	cursor: pointer;
	transition:
		transform 0.2s ease,
		box-shadow 0.2s ease;
}

.image-modal-img {
	max-width: 100%;
	max-height: calc(80vh - 64px);
	width: auto;
	height: auto;
	border-radius: 8px;
	display: block;
}
</style>
