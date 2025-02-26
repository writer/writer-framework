<script setup lang="ts">
import { useTemplateRef } from "vue";

const input = useTemplateRef("input");

const emits = defineEmits({
	selected: (files: FileList) => Array.isArray(files) && files.length > 0,
});

function onFileUploaded() {
	if (input.value.files?.length) emits("selected", input.value.files);
}
</script>

<template>
	<form class="BuilderCodePanelFileUploadBtn">
		<input
			v-show="false"
			ref="input"
			type="file"
			multiple="true"
			@change="onFileUploaded"
		/>
		<button
			class="BuilderCodePanelFileUploadBtn__btn"
			type="button"
			@click="input.click()"
		>
			<i class="material-symbols-outlined">upload</i>
			Upload
		</button>
	</form>
</template>

<style scoped>
.BuilderCodePanelFileUploadBtn__btn {
	height: 32px;
	padding: 8px;

	cursor: pointer;
	background-color: transparent;
	color: var(--wdsColorBlue5);
	font-size: 12px;
	border: none;

	display: flex;
	justify-content: flex-start;
	align-items: center;
	gap: 4px;

	font-weight: 500;
}
</style>
