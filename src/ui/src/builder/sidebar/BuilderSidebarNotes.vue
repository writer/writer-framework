<template>
	<BuilderSidebarPanel v-model="query" class="BuilderSidebarNotes">
		<ul class="BuilderSidebarNotes__notes">
			<BuilderSidebarNotesItem
				v-for="note of notes"
				:key="note.id"
				:component="note"
			/>
		</ul>
	</BuilderSidebarPanel>
</template>

<script setup lang="ts">
import { computed, inject, ref } from "vue";
import BuilderSidebarPanel from "./BuilderSidebarPanel.vue";
import injectionKeys from "@/injectionKeys";
import { useBuilderNotes } from "../useBuilderNotes";
import BuilderSidebarNotesItem from "./BuilderSidebarNotesItem.vue";

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
</style>
