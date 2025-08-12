<script setup lang="ts">
import { computed } from "vue";

const props = defineProps({
	status: { type: Boolean },
	count: { type: Number, required: true },
	completionStyle: { type: String, required: false, default: undefined },
});

defineEmits({
	click: () => true,
});

const content = computed(() => {
	if (props.count === 1) return "1 output";
	return `${props.count} outputs`;
});
</script>

<template>
	<div class="BlueprintsNodeLogs">
		<button
			class="BlueprintsNodeLogs__btn"
			:class="{
				'BlueprintsNodeLogs__btn--success':
					completionStyle == 'success',
				'BlueprintsNodeLogs__btn--skipped':
					completionStyle == 'skipped',
				'BlueprintsNodeLogs__btn--stopped':
					completionStyle == 'stopped',
				'BlueprintsNodeLogs__btn--error': completionStyle == 'error',
			}"
			:data-writer-unselectable="true"
			type="button"
			@click="$emit('click')"
		>
			{{ content }}
		</button>
	</div>
</template>

<style scoped>
.BlueprintsNodeLogs {
	display: flex;
}
.BlueprintsNodeLogs__btn {
	border-radius: 4px;
	border: none;
	padding: 4px 8px;
	cursor: pointer;
}
.BlueprintsNodeLogs__btn--success {
	background: var(--wdsColorGreen3) !important;
}

.BlueprintsNodeLogs__btn--skipped {
	background: var(--wdsColorGray3) !important;
}

.BlueprintsNodeLogs__btn--stopped {
	background: var(--wdsColorGray3) !important;
}

.BlueprintsNodeLogs__btn--error {
	background: var(--wdsColorOrange2) !important;
}
</style>
