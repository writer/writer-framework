<template>
	<div class="SharedFile">
		<LoadingSymbol v-if="status === 'uploading'" />
		<div v-else class="SharedFile__icon">
			<WdsIcon name="file-check" />
		</div>
		<span class="SharedFile__name" :title="name">
			{{ name }}
		</span>
		<div v-if="areActionsShown" class="SharedFile__actions">
			<WdsTag v-if="isSizeShown" variant="normal" :text="formattedSize" />
			<WdsButton
				v-if="isDownloadButtonShown"
				variant="tertiary"
				size="smallIcon"
				data-writer-tooltip="Download File"
				@click="$emit('download')"
			>
				<WdsIcon name="download" />
			</WdsButton>
		</div>
	</div>
</template>

<script setup lang="ts">
import { computed, PropType } from "vue";
import prettyBytes from "pretty-bytes";
import WdsButton from "@/wds/WdsButton.vue";
import WdsIcon from "@/wds/WdsIcon.vue";
import WdsTag from "@/wds/WdsTag.vue";
import LoadingSymbol from "@/renderer/LoadingSymbol.vue";

const props = defineProps({
	status: {
		type: String as PropType<"uploading" | "ready">,
		required: true,
	},
	name: {
		type: String,
		default: "",
	},
	size: {
		type: Number,
		default: 0,
	},
});

defineEmits({
	download: () => true,
});

const isSizeShown = computed<boolean>(() => props.size > 0);
const isDownloadButtonShown = computed<boolean>(() => props.status === "ready");

const areActionsShown = computed<boolean>(
	() => isSizeShown.value || isDownloadButtonShown.value,
);

const formattedSize = computed<string>(() => prettyBytes(props.size));
</script>

<style scoped>
.SharedFile {
	position: relative;
	padding: 8px 10px;
	gap: 8px;
	display: grid;
	grid-template-columns: auto 1fr;
	align-items: center;
	min-height: 48px;
	background-color: var(--wdsColorBlue1);
	border: 1px solid transparent;
	border-radius: 8px;
}

.SharedFile:has(.SharedFile__actions) {
	grid-template-columns: auto 1fr auto;
}

.SharedFile__icon {
	display: flex;
	align-items: center;
	justify-content: center;
	width: 24px;
	height: 24px;
	color: var(--wdsColorWhite);
	background-color: var(--wdsColorBlue5);
	border-radius: 4px;
}

.SharedFile__name {
	cursor: default;
	font-size: 14px;
	font-weight: normal;
	line-height: 180%;
	overflow: hidden;
	white-space: nowrap;
	text-overflow: ellipsis;
	text-align: start;
	color: var(--wdsColorBlack);
}

.SharedFile__actions {
	gap: 8px;
	display: flex;
	align-items: center;
}
</style>
