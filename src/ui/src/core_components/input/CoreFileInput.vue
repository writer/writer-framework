<template>
	<BaseInputWrapper
		ref="rootInstance"
		:label="!processingFiles ? fields.label.value : null"
		class="CoreFileInput"
	>
		<div class="main">
			<input
				v-if="!processingFiles"
				ref="fileEl"
				type="file"
				:multiple="allowMultipleFilesFlag"
				@change="fileChange($event as InputEvent)"
			/>
			<div v-if="message || processingFiles" class="status">
				<LoadingSymbol
					v-if="processingFiles"
					class="loadingSymbol"
				></LoadingSymbol>
				<span v-if="processingFiles"
					>Processing {{ processingFiles.join(", ") }}...</span
				>
				<span v-if="message">{{ message }}</span>
			</div>
		</div>
	</BaseInputWrapper>
</template>

<script lang="ts">
import { FieldType } from "../../writerTypes";
import { cssClasses } from "../../renderer/sharedStyleFields";
import BaseInputWrapper from "../base/BaseInputWrapper.vue";
import { ComponentPublicInstance } from "vue";

const MAX_FILE_SIZE = 200 * 1024 * 1024;

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
		name: "File Input",
		description,
		category: "Input",
		fields: {
			label: {
				name: "Label",
				init: "Input Label",
				type: FieldType.Text,
			},
			allowMultipleFiles: {
				name: "Allow multiple files",
				default: "no",
				type: FieldType.Text,
				options: {
					yes: "Yes",
					no: "No",
				},
			},
			cssClasses,
		},
		events: {
			"wf-file-change": {
				desc: "Capture changes to this control.",
				stub: onChangeHandlerStub,
				bindable: true,
			},
		},
	},
};
</script>

<script setup lang="ts">
import LoadingSymbol from "../../renderer/LoadingSymbol.vue";
import { computed, inject, Ref, ref, watch } from "vue";
import injectionKeys from "../../injectionKeys";
import { useFormValueBroker } from "../../renderer/useFormValueBroker";

const fields = inject(injectionKeys.evaluatedFields);
const rootInstance = ref<ComponentPublicInstance | null>(null);
const fileEl: Ref<HTMLInputElement> = ref(null);
const message: Ref<string> = ref(null);
const wf = inject(injectionKeys.core);
const instancePath = inject(injectionKeys.instancePath);
const processingFiles: Ref<string[]> = ref(null);

const { formValue, handleInput } = useFormValueBroker(
	wf,
	instancePath,
	rootInstance,
);

const allowMultipleFilesFlag = computed(() => {
	return fields.allowMultipleFiles.value == "yes" ? true : undefined;
});

const encodeFile = async (file: File) => {
	var reader = new FileReader();
	reader.readAsDataURL(file);

	return new Promise((resolve, reject) => {
		reader.onload = () => resolve(reader.result);
		reader.onerror = () => reject(reader.error);
	});
};

const fileChange = async (ev: InputEvent) => {
	const el = ev.target as HTMLInputElement;
	if (!el.files || el.files.length == 0) return;

	const getValue = async () => {
		let accumSize = 0;
		message.value = null;
		const encodedFiles = Promise.all(
			Array.from(el.files).map(async (f) => {
				accumSize += f.size;
				const fileItem = {
					name: f.name,
					type: f.type,
					data: await encodeFile(f),
				};
				return fileItem;
			}),
		);
		if (accumSize > MAX_FILE_SIZE) {
			message.value = `Files are too big. Total size limit is ${Math.floor(MAX_FILE_SIZE / Math.pow(1024, 2))}mb.`;
			return [];
		}
		return encodedFiles;
	};

	processingFiles.value = Array.from(el.files).map((file) => file.name);
	formValue.value = getValue();

	const customCallback = () => {
		processingFiles.value = null;
	};

	handleInput(getValue(), "wf-file-change", customCallback);
};

watch(formValue, (newValue: string) => {
	if (typeof newValue === "undefined" && fileEl.value) {
		fileEl.value.value = "";
	}
});
</script>

<style scoped>
@import "../../renderer/sharedStyles.css";
@import "../../renderer/colorTransformations.css";

.CoreFileInput {
	width: 100%;
}

.main {
	display: flex;
	flex-direction: column;
	gap: 16px;
}

input {
	max-width: 70ch;
	margin: 0;
	border: 1px solid var(--separatorColor);
	border-radius: 8px;
	padding: 8.25px;
	font-size: 0.875rem;
	width: fit-content;
	outline: none;
}

input:focus {
	border: 1px solid var(--softenedAccentColor);
	box-shadow: 0px 0px 0px 3px rgba(81, 31, 255, 0.05);
}

.status {
	display: flex;
	align-items: center;
	gap: 12px;
	min-height: 36px;
}

.status .loadingSymbol {
	flex: 0 0 24px;
}

.status span {
	text-overflow: ellipsis;
	white-space: nowrap;
	overflow: hidden;
}
</style>
