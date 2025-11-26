<template>
	<div class="actions">
		<WdsButton
			v-if="entry.entryType === 'execution'"
			variant="neutral"
			size="small"
			type="button"
			@click="$emit('re-run')"
		>
			<WdsIcon name="play" />
			Re-run
		</WdsButton>
		<WdsButton
			v-if="entry.entryType === 'execution'"
			variant="neutral"
			size="small"
			type="button"
			@click="$emit('go-to-trigger')"
		>
			<WdsIcon name="locate" />
			Go to Trigger
		</WdsButton>
		<WdsButton
			variant="neutral"
			size="small"
			type="button"
			@click="$emit('download')"
		>
			<WdsIcon name="download" />
			Download JSON
		</WdsButton>
		<SharedCopyClipboardButton
			:value="outputsJson"
			text="Copy Output"
			variant="neutral"
			size="small"
			label="Copy output to clipboard"
		/>
	</div>
</template>

<script setup lang="ts">
import { computed, PropType } from "vue";
import WdsButton from "@/wds/WdsButton.vue";
import WdsIcon from "@/wds/WdsIcon.vue";
import SharedCopyClipboardButton from "@/components/shared/SharedCopyClipboardButton.vue";
import type { UnifiedEntry } from "../BuilderJournal.vue";

const props = defineProps({
	entry: { type: Object as PropType<UnifiedEntry>, required: true },
});

defineEmits<{
	"re-run": () => true;
	"go-to-trigger": () => true;
	download: () => true;
}>();

const outputsJson = computed(() => {
	if (props.entry.entryType === "execution") {
		return JSON.stringify(props.entry.blockOutputs, null, 2);
	}
	return JSON.stringify(
		{
			stdout: props.entry.stdout,
			logs: props.entry.logs,
		},
		null,
		2,
	);
});
</script>

<style scoped>
.actions {
	display: flex;
	gap: 8px;
	padding: 16px 20px;
	border-bottom: 1px solid var(--wdsColorGray2);
	flex-wrap: wrap;
}
</style>
