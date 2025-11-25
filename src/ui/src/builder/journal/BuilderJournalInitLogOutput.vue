<template>
	<div>
		<div v-if="entry.stdout" class="output-block output-block--init">
			<h4 class="output-block__title">Stdout</h4>
			<pre class="output-block__log-content">{{ entry.stdout }}</pre>
		</div>
		<div v-if="entry.logs" class="output-block output-block--init">
			<h4 class="output-block__title">Logs</h4>
			<pre class="output-block__log-content">{{ entry.logs }}</pre>
		</div>
		<div
			v-if="!entry.stdout && !entry.logs"
			class="output-block output-block--init"
		>
			<p style="color: var(--wdsColorGray5); margin: 0">
				No logs captured during initialization.
			</p>
		</div>
	</div>
</template>

<script setup lang="ts">
import type { PropType } from "vue";
import type { InitLogEntry } from "../BuilderJournal.vue";

defineProps({
	entry: { type: Object as PropType<InitLogEntry>, required: true },
});
</script>

<style scoped>
.output-block {
	border: 1px solid var(--wdsColorGray3);
	border-radius: 6px;
	padding: 16px;
	margin-bottom: 16px;
	background: var(--wdsColorGray1);
}

.output-block--init {
	background: var(--wdsColorPurple1);
	border-color: var(--wdsColorPurple3);
}

.output-block--init .output-block__title {
	color: var(--wdsColorPurple6);
	font-size: 14px;
	font-weight: 600;
	margin: 0 0 8px 0;
}

.output-block__log-content {
	margin: 0;
	padding: 12px;
	background: var(--wdsColorWhite);
	border: 1px solid var(--wdsColorPurple2);
	border-radius: 4px;
	font-family: "Courier New", Courier, monospace;
	font-size: 12px;
	white-space: pre-wrap;
	word-break: break-word;
	color: var(--wdsColorGray7);
	overflow-x: auto;
	max-height: 400px;
	overflow-y: auto;
}
</style>
