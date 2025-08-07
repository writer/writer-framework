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
	cursor: pointer;

	/* we are using outline instead of background to make the dot looks smaller */
	outline: 4px var(--builderBackgroundColor) solid;
	outline-offset: -8px;
}

.BlueprintsNodeOutput__ball.success {
	outline-color: var(--wdsColorGreen5);
}

.BlueprintsNodeOutput__ball.error {
	outline-color: var(--wdsColorOrange5);
}

.BlueprintsNodeOutput__ball.dynamic {
	outline-color: var(--wdsColorPurple4);
}

.BlueprintsNodeOutput__ball.branching {
	outline-color: var(--wdsColorPurple4);
}
</style>
