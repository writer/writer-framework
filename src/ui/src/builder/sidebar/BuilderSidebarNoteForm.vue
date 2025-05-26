<script setup lang="ts">
import { inject, PropType, ref } from "vue";
import injectionKeys from "@/injectionKeys";
import { Component } from "@/writerTypes";
import WdsTextareaInput from "@/wds/WdsTextareaInput.vue";
import WdsButton from "@/wds/WdsButton.vue";

const props = defineProps({
	component: { type: Object as PropType<Component>, required: true },
	autofocus: { type: Boolean },
});

defineEmits({
	submit: (content: string) => typeof content === "string",
});

const notesManager = inject(injectionKeys.notesManager);

const content = ref(notesManager.getNoteContent(props.component));
</script>

<template>
	<div class="BuilderSidebarNoteForm">
		<WdsTextareaInput
			v-model="content"
			class="BuilderSidebarNoteForm__input"
			:autofocus="autofocus"
		/>
		<WdsButton
			class="BuilderSidebarNoteForm__submit"
			variant="secondary"
			size="smallIcon"
			@click="$emit('submit', content)"
		>
			<span class="material-symbols-outlined">send</span>
		</WdsButton>
	</div>
</template>

<style scoped>
.BuilderSidebarNoteForm {
	position: relative;
}

.BuilderSidebarNoteForm__input {
	resize: vertical;
	padding-bottom: 40px;
}

.BuilderSidebarNoteForm__submit {
	position: absolute;
	bottom: 8px;
	right: 8px;
}
</style>
