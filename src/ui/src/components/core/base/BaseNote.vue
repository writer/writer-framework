<script setup lang="ts">
import injectionKeys from "@/injectionKeys";
import { inject, computed } from "vue";
// @ts-expect-error importing SVG
import defaultSvg from "@/assets/note-default.svg";
// @ts-expect-error importing SVG
import hoverSvg from "@/assets/note-hover.svg";
// @ts-expect-error importing SVG
import activeSvg from "@/assets/note-active.svg";
// @ts-expect-error importing SVG
import newSvg from "@/assets/note-new.svg";
// @ts-expect-error importing SVG
import cursorSvg from "@/assets/note-cursor.svg";

const props = defineProps({
	componentId: { type: String, required: true },
});
const wf = inject(injectionKeys.core);
const notesManager = inject(injectionKeys.notesManager);

const component = computed(() => wf.getComponentById(props.componentId));

const { state } = notesManager.useNoteInformation(component);

const src = computed(() => {
	switch (state.value) {
		case "hover":
			return hoverSvg;
		case "active":
			return activeSvg;
		case "new":
			return newSvg;
		case "cursor":
			return cursorSvg;
		default:
			return defaultSvg;
	}
});

function onClick() {
	notesManager.selectNote(props.componentId, "show");
}
</script>

<template>
	<button
		type="button"
		class="BuilderNote"
		data-writer-unselectable="true"
		@mouseenter="notesManager.hoveredNoteId.value = componentId"
		@mouseleave="notesManager.hoveredNoteId.value = undefined"
		@click="onClick"
	>
		<img :src="src" width="32" height="32" />
	</button>
</template>

<style lang="css" scoped>
.BuilderNote {
	position: absolute;
	cursor: pointer;

	background-color: transparent;
	border: none;
}
</style>
