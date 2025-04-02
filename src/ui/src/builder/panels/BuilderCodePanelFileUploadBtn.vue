<script setup lang="ts">
import WdsButtonLink from "@/wds/WdsButtonLink.vue";
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
		<WdsButtonLink
			left-icon="upload"
			text="Upload"
			@click="input.click()"
		/>
	</form>
</template>
