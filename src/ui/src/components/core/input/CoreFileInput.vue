<template>
	<BaseInputWrapper
		ref="rootInstance"
		:label="fields.label.value"
		class="CoreFileInput"
	>
		<div class="main">
			<SharedDropZone
				:multiple="isMultipleFilesAllowed"
				:accepted-file-types="acceptedFileTypes"
				:total-size-limit="MAX_FILE_SIZE"
				@drop="handleUploadFiles"
			/>
			<ul v-if="files.length > 0" class="file-list">
				<li v-for="uiFile of files" :key="uiFile.id">
					<SharedFile
						:status="isUploading ? 'uploading' : 'ready'"
						:name="uiFile.name"
						:size="uiFile.size"
						@download="downloadFile(uiFile.file)"
					/>
				</li>
			</ul>
			<div v-if="uploadingErrorMessage" class="status">
				<span>{{ uploadingErrorMessage }}</span>
			</div>
		</div>
	</BaseInputWrapper>
</template>

<script lang="ts">
import { ComponentPublicInstance } from "vue";
import { createBooleanField, cssClasses } from "@/renderer/sharedStyleFields";
import { FieldType } from "@/writerTypes";
import BaseInputWrapper from "../base/BaseInputWrapper.vue";

const description = "A user input component that allows users to upload files.";

const onChangeHandlerStub = `
def onchange_handler(state, payload):

	# An array of dictionaries is provided in the payload
	# The dictionaries have the properties name, type and data
    # The data property is a file-like object

    uploaded_files = payload
    for i, uploaded_file in enumerate(uploaded_files):
		name = uploaded_file.get("name")
        file_data = uploaded_file.get("data")
        with open(f"{name}-{i}.jpeg", "wb") as file_handle:
            file_handle.write(file_data)`.trim();

export default {
	writer: {
		name: "File input",
		description,
		category: "Input",
		fields: {
			label: {
				name: "Label",
				init: "Input Label",
				type: FieldType.Text,
			},
			allowFileTypes: {
				name: "Allowed file types",
				type: FieldType.Text,
				init: [
					".pdf",
					".txt",
					".doc",
					"application/msword",
					"application/vnd.openxmlformats-officedocument.wordprocessingml.document",
				].join(", "),
				desc: "Provides hints for browsers to select the correct file types. You can specify extensions and MIME types separated by comma, or leave empty to accept any file.",
			},
			allowMultipleFiles: createBooleanField({
				name: "Allow multiple files",
				default: "no",
			}),
			cssClasses,
		},
		events: {
			"wf-file-change": {
				desc: "Capture changes to this control.",
				stub: onChangeHandlerStub,
				bindable: true,
				eventPayloadExample: [
					{
						name: "hello.txt",
						type: "text/plain",
						data: "data:text/plain;base64,SGVsbG8gd29ybGQK",
					},
				],
			},
		},
	},
};
</script>

<script setup lang="ts">
import { computed, inject, onMounted, ref } from "vue";
import prettyBytes from "pretty-bytes";
import injectionKeys from "@/injectionKeys";
import { useFormValueBroker } from "@/renderer/useFormValueBroker";
import { useFilesEncoder } from "@/composables/useFilesEncoder/useFilesEncoder";
import SharedFile from "@/components/shared/SharedFile.vue";
import SharedDropZone from "@/components/shared/SharedDropZone.vue";

const fields = inject(injectionKeys.evaluatedFields);
const rootInstance = ref<ComponentPublicInstance | null>(null);
const wf = inject(injectionKeys.core);
const instancePath = inject(injectionKeys.instancePath);

const { formValue, handleInput } = useFormValueBroker(
	wf,
	instancePath,
	rootInstance,
);

const acceptedFileTypes = computed<string[]>(() =>
	(fields.allowFileTypes?.value ?? "").split(","),
);

const isMultipleFilesAllowed = computed<boolean>(() =>
	Boolean(fields.allowMultipleFiles.value),
);

const { files, calcTotalSize, replaceFiles, encodeFiles, decodeFiles } =
	useFilesEncoder({
		multiple: isMultipleFilesAllowed,
	});

onMounted(async () => {
	if (Array.isArray(formValue.value)) {
		const { decodedFiles } = await decodeFiles(formValue.value);

		replaceFiles(decodedFiles);
	}
});

const MAX_FILE_SIZE = 200 * 1024 * 1024;
const isUploading = ref(false);
const uploadingErrorMessage = ref<string | null>(null);
async function handleUploadFiles(files: File[]) {
	if (isUploading.value) return;

	if (calcTotalSize(files) > MAX_FILE_SIZE) {
		uploadingErrorMessage.value = `Files are too big. Total size limit is ${prettyBytes(MAX_FILE_SIZE)}.`;

		return;
	}

	isUploading.value = true;
	uploadingErrorMessage.value = null;

	replaceFiles(files);

	const { encodedFiles } = await encodeFiles();

	if (encodedFiles.length === 0) {
		isUploading.value = false;
		return;
	}

	handleInput(encodedFiles, "wf-file-change");

	isUploading.value = false;
}

function downloadFile(file: File) {
	const blobURL = window.URL.createObjectURL(file);

	const link = document.createElement("a");
	link.href = blobURL;
	link.download = file.name;
	link.click();
	link.remove();

	setTimeout(() => {
		window.URL.revokeObjectURL(blobURL);
	}, 200);
}
</script>

<style scoped>
@import "@/renderer/sharedStyles.css";
@import "@/renderer/colorTransformations.css";

.CoreFileInput {
	width: 100%;
}

.main {
	display: flex;
	flex-direction: column;
	gap: 16px;
}

.file-list {
	list-style: none;
	display: flex;
	flex-direction: column;
	gap: 12px;
}

.file-list li {
	margin-left: 0;
}

.status {
	display: flex;
	align-items: center;
	gap: 12px;
	min-height: 36px;
}

.status span {
	text-overflow: ellipsis;
	white-space: nowrap;
	overflow: hidden;
}
</style>
