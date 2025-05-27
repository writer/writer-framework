<script setup lang="ts">
import { computed, inject, ref } from "vue";
import injectionKeys from "@/injectionKeys";
import type { Component } from "@/writerTypes";
import BuilderSidebarPanel from "./BuilderSidebarPanel.vue";
import BuilderSidebarNote from "./BuilderSidebarNote.vue";
import BuilderSidebarNotesEmpty from "./BuilderSidebarNotesEmpty.vue";
import BuilderSidebarNoteForm from "./BuilderSidebarNoteForm.vue";
import { useComponentActions } from "../useComponentActions";

const wf = inject(injectionKeys.core);
const wfbm = inject(injectionKeys.builderManager);
const {
	selectedNote,
	selectNote,
	selectedNoteMode,
	selectedNoteId,
	getAllNotes,
	searchNotes,
	deleteNote,
	hoveredNoteId,
	useNoteInformation,
} = inject(injectionKeys.notesManager);

const { setContentValue } = useComponentActions(wf, wfbm);

const query = ref("");

const notes = computed(() => Array.from(getAllNotes()).toSorted(sortNotes));
const notesQuery = computed(() =>
	Array.from(searchNotes(query.value)).toSorted(sortNotes),
);

const hideSearchBar = computed(() => {
	if (selectedNote.value) return true;
	if (notes.value.length === 0) return true;
	return false;
});

function sortNotes(a: Component, b: Component) {
	const aDate = useNoteInformation(a).createdAt.value;
	const bDate = useNoteInformation(b).createdAt.value;
	return new Date(bDate).getTime() - new Date(aDate).getTime();
}

function getNoteState(component: Component) {
	return useNoteInformation(component).state.value;
}

function onSaveNoteContent(content: string) {
	setContentValue(selectedNoteId.value, "content", content);
	selectNote(undefined);
}
</script>

<template>
	<BuilderSidebarPanel
		v-model="query"
		class="BuilderSidebarNotes"
		:hide-search-bar="hideSearchBar"
	>
		<div v-if="selectedNote" class="BuilderSidebarNotes__note">
			<BuilderSidebarNoteForm
				v-if="selectedNoteMode === 'edit'"
				:component="selectedNote"
				autofocus
				@submit="onSaveNoteContent"
			/>
			<BuilderSidebarNote
				v-else
				:component="selectedNote"
				@go-back="selectNote(undefined)"
				@edit="selectNote(selectedNoteId, 'edit')"
				@delete="deleteNote(selectedNoteId)"
			/>
		</div>
		<BuilderSidebarNotesEmpty v-else-if="notesQuery.length === 0" />
		<div v-else class="BuilderSidebarNotes__notes">
			<BuilderSidebarNote
				v-for="note of notesQuery"
				:key="note.id"
				:component="note"
				class="BuilderSidebarNotes__notes__note"
				:class="{
					'BuilderSidebarNotes__notes__note--hover':
						getNoteState(note) === 'hover',
				}"
				excerpt
				@select="selectNote(note.id, 'show')"
				@edit="selectNote(note.id, 'edit')"
				@delete="deleteNote(note.id)"
				@mouseenter="hoveredNoteId = note.id"
				@mouseleave="hoveredNoteId = undefined"
			/>
		</div>
	</BuilderSidebarPanel>
</template>

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
.BuilderSidebarNotes__notes__note:hover,
.BuilderSidebarNotes__notes__note--hover {
	background-color: var(--wdsColorBlue1);
}

.BuilderSidebarNotes__note {
	padding: 16px;
}

.BuilderSidebarNotes__note:deep(textarea) {
	field-sizing: content;
}
</style>
