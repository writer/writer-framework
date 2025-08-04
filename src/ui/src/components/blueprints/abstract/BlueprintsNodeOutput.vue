<script setup lang="ts">
import type { WriterComponentDefinitionOut } from "@/writerTypes";
import { PropType } from "vue";

defineProps({
	outId: { type: String, required: true },
	out: {
		type: Object as PropType<WriterComponentDefinitionOut>,
		required: true,
	},
	displayLabel: { type: Boolean },
});

defineEmits({
	click: () => true,
});
</script>

<template>
	<div class="BlueprintsNodeOutput">
		<template v-if="displayLabel">
			{{ out.name }}
		</template>
		<div
			class="BlueprintsNodeOutput__ball"
			:class="out.style"
			:data-writer-socket-id="outId"
			:data-writer-unselectable="true"
			@click.capture.stop
			@mousedown.capture.stop="$emit('click')"
		></div>
	</div>
</template>

<style lang="css" scoped>
.BlueprintsNodeOutput {
	display: flex;
	gap: 8px;
	align-items: center;
	justify-content: right;
	font-size: 12px;
	font-style: normal;
	font-weight: 400;
	color: var(--wdsColorGray5);
	font-feature-settings:
		"liga" off,
		"clig" off;
}

.BlueprintsNodeOutput__ball {
	margin-right: -9px;

	height: 16px;
	width: 16px;
	border-radius: 50%;
	border: 1px solid var(--builderBackgroundColor);
	cursor: pointer;
}

.BlueprintsNodeOutput__ball.success {
	background: var(--wdsColorGreen5);
}

.BlueprintsNodeOutput__ball.error {
	background: var(--wdsColorOrange5);
}

.BlueprintsNodeOutput__ball.dynamic {
	background: var(--wdsColorPurple4);
}

.BlueprintsNodeOutput__ball.branching {
	background: var(--wdsColorPurple4);
}
</style>
