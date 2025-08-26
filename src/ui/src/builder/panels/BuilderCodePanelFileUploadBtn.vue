<script setup lang="ts">
import WdsButtonLink from "@/wds/WdsButtonLink.vue";
import { useTemplateRef } from "vue";

const input = useTemplateRef("input");

const emits = defineEmits({
	selected: (files: File[]) => Array.isArray(files) && files.length > 0,
});

function onFileUploaded() {
	const { files } = input.value;

	if (files instanceof FileList && files.length > 0) {
		emits("selected", Array.from(files));

		// allows selecting the same files again to retrigger `change` event
		input.value.value = "";
	}
}
</script>

<template>
	<form class="BuilderCodePanelFileUploadBtn">
		<input
			v-show="false"
			ref="input"
			type="file"
			multiple
			@change="onFileUploaded"
		/>
		<WdsButtonLink
			left-icon="upload"
			text="Upload"
			@click="input.click()"
		/>
	</form>
</template>
