<template>
	<BuilderSidebarPanel v-model="query" class="BuilderSidebarNotes">
		<ul class="BuilderSidebarNotes__notes">
			<li
				v-for="note of notes"
				:key="note.id"
				class="BuilderSidebarNotes__notes__note"
				:data-note-id="note.id"
			>
				Note : {{ note.id }}
			</li>
		</ul>
	</BuilderSidebarPanel>
</template>

<script setup lang="ts">
import { computed, inject, ref } from "vue";
import BuilderSidebarPanel from "./BuilderSidebarPanel.vue";
import injectionKeys from "@/injectionKeys";
import { useBuilderNotes } from "../useBuilderNotes";

const wf = inject(injectionKeys.core);
const wfbm = inject(injectionKeys.builderManager);
const query = ref("");
const builderNotes = useBuilderNotes(wf, wfbm);

const notes = computed(() => Array.from(builderNotes.getAllNotes()));
</script>

<style scoped>
.BuilderSidebarNotes__notes {
	border-top: 1px solid var(--wdsColorGray2);
	list-style: none;
	display: flex;
	flex-direction: column;
}

.BuilderSidebarNotes:deep(.BuilderSidebarPanel__main) {
	padding-left: 0;
	padding-right: 0;
}

.BuilderSidebarNotes__notes__note {
	border-bottom: 1px solid var(--wdsColorGray2);
	padding: 16px;
}
.BuilderSidebarNotes__notes__note:hover {
	background-color: var(--wdsColorBlue1);
}
</style>
