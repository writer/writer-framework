<template>
	<SharedMoreDropdown
		class="BuilderHeaderMoreDropdown"
		trigger-variant="secondary"
		:options="options"
		@select="onSelect"
	/>
	<input
		v-show="false"
		ref="exportInput"
		type="file"
		accept=".zip,application/zip"
		@change="importConfirmShown = true"
	/>
	<WdsModal
		v-if="importConfirmShown"
		:actions="importModalActions"
		title="Are you sure you want to continue?"
		description="Your current work will be replaced with the agent in the zip file. This includes replacement of current pages, blueprints, local scripts, and custom assets."
		size="normal"
	>
		<WdsCheckbox
			v-model="importConfirmCheckbox"
			label="Yes, I want to replace the current agent with the imported file"
		/>
	</WdsModal>
</template>

<script setup lang="ts">
import { computed, inject, ref, useTemplateRef } from "vue";
import injectionKeys from "@/injectionKeys";
import { useToasts } from "./useToast";
import { useWriterTracking } from "@/composables/useWriterTracking";
import SharedMoreDropdown, {
	Option,
} from "@/components/shared/SharedMoreDropdown.vue";
import WdsModal, { ModalAction } from "@/wds/WdsModal.vue";
import WdsCheckbox from "@/wds/WdsCheckbox.vue";

const options: Option[] = [
	{ label: "Import agent .zip file", value: "import", icon: "upload" },
	{ label: "Download agent .zip file", value: "export", icon: "download" },
];

const wf = inject(injectionKeys.core);

const exportInput = useTemplateRef("exportInput");

const tracking = useWriterTracking(wf);
const toasts = useToasts();

const importInProgress = ref(false);
const importConfirmShown = ref(false);
const importConfirmCheckbox = ref(false);

const importModalActions = computed<ModalAction[]>(() => [
	{
		disabled: importInProgress.value,
		desc: "Cancel",
		fn: () => {
			importConfirmCheckbox.value = false;
			importConfirmShown.value = false;
		},
	},
	{
		disabled: importInProgress.value || !importConfirmCheckbox.value,
		loading: importInProgress.value,
		desc: "Import",
		fn: importModalConfirm,
	},
]);

async function exportProject() {
	tracking.track("nav_export_clicked");

	if (!exportInput.value) return;
	const response = await fetch("./api/export");
	if (!response.ok) {
		throw new Error("Failed to connect to export API");
	}
	const blob = await response.blob();
	const url = window.URL.createObjectURL(blob);
	const a = document.createElement("a");
	a.href = url;
	a.download = "export.zip"; // Set the filename here
	document.body.appendChild(a);
	a.click();
	document.body.removeChild(a);
	window.URL.revokeObjectURL(url);
}

async function importModalConfirm() {
	tracking.track("nav_import_clicked");

	if (!exportInput.value) return;
	const file = exportInput.value.files[0];
	if (!file) return;

	importInProgress.value = true;

	try {
		// Prepare form data
		const formData = new FormData();
		formData.append("file", file);

		// Send POST request
		const response = await fetch("./api/import", {
			method: "POST",
			body: formData,
		});
		if (!response.ok) {
			throw new Error("Failed to connect to import API");
		}
		importConfirmShown.value = false;
		toasts.pushToast({
			type: "success",
			message: "Project imported successfully.",
		});
	} catch (e) {
		toasts.pushToast({
			type: "error",
			message:
				"Failed to import the project: " +
				(e instanceof Error ? e.message : String(e)),
		});
	} finally {
		importInProgress.value = false;
	}
}

async function onSelect(key: string) {
	if (key === "export") {
		try {
			await exportProject();
		} catch (e) {
			toasts.pushToast({
				message: `Failed to export the project: ${e}`,
				type: "error",
			});
		}
	} else if (key === "import") {
		exportInput.value.value = "";
		exportInput.value.click();
	}
}
</script>

<style scoped>
.BuilderHeaderMoreDropdown:deep(.BuilderMoreDropdown__dropdown) {
	min-width: 200px;
}
</style>
