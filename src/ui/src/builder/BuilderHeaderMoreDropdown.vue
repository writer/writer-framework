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
		<div
			v-if="importErrorSummary"
			class="BuilderHeaderMoreDropdown__importError"
		>
			<p class="BuilderHeaderMoreDropdown__importError__header">
				Failed to import the agent
			</p>

			<p class="BuilderHeaderMoreDropdown__importError__summary">
				{{ importErrorSummary }}
			</p>

			<details
				v-if="importErrorDetails"
				class="BuilderHeaderMoreDropdown__importError__details"
			>
				<summary>Show details</summary>
				<pre class="BuilderHeaderMoreDropdown__importError__trace">{{
					importErrorDetails
				}}</pre>
			</details>
		</div>
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

const options = computed<Option[]>(() => [
	{ label: "Import agent .zip file", value: "import", icon: "upload" },
	{ label: "Download agent .zip file", value: "export", icon: "download" },
	{
		label: socketTimeout.preventTasks.value.has("stayAwake")
			? "Turn off stay awake mode"
			: "Keep session awake",
		value: "awake",
		icon: "coffee",
	},
]);

const wf = inject(injectionKeys.core);
const socketTimeout = inject(injectionKeys.socketTimeout);

const exportInput = useTemplateRef("exportInput");

const tracking = useWriterTracking(wf);
const toasts = useToasts();

const importInProgress = ref(false);
const importConfirmShown = ref(false);
const importConfirmCheckbox = ref(false);
const importErrorSummary = ref("");
const importErrorDetails = ref("");

const importModalActions = computed<ModalAction[]>(() => [
	{
		disabled: importInProgress.value,
		desc: "Cancel",
		fn: () => {
			importConfirmCheckbox.value = false;
			importConfirmShown.value = false;
			importErrorSummary.value = "";
			importErrorDetails.value = "";
		},
	},
	{
		disabled: !importConfirmCheckbox.value,
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
	importErrorSummary.value = "";
	importErrorDetails.value = "";

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
			const parsed = await response.json();
			importErrorSummary.value = parsed?.detail?.summary;
			importErrorDetails.value = parsed?.detail?.details;
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
	switch (key) {
		case "export":
			try {
				await exportProject();
			} catch (e) {
				toasts.pushToast({
					message: `Failed to export the project: ${e}`,
					type: "error",
				});
			}
			break;
		case "import":
			exportInput.value.value = "";
			exportInput.value.click();
			break;
		case "awake":
			socketTimeout?.togglePreventTaskId("stayAwake");
	}
}
</script>

<style scoped>
.BuilderHeaderMoreDropdown:deep(.SharedMoreDropdown__dropdown) {
	min-width: 220px;
}

.BuilderHeaderMoreDropdown__importError {
	margin-top: 16px;
	padding: 12px 14px;
	border-radius: 8px;
	background: rgba(255, 149, 0, 0.08);
	border: 1px solid rgba(255, 149, 0, 0.35);
	grid-column: 2 / 4;
}

.BuilderHeaderMoreDropdown__importError__header {
	font-weight: 600;
	color: var(--wdsColorOrange4);
	font-size: 14px;
}

.BuilderHeaderMoreDropdown__importError__summary {
	margin-top: 6px;
	font-size: 14px;
}

.BuilderHeaderMoreDropdown__importError__details {
	margin-top: 10px;
}

.BuilderHeaderMoreDropdown__importError__details summary {
	cursor: pointer;
	font-size: 12px;
	user-select: none;
}

.BuilderHeaderMoreDropdown__importError__details summary:hover {
	text-decoration: underline;
}

.BuilderHeaderMoreDropdown__importError__trace {
	margin-top: 8px;
	max-height: 220px;
	overflow: auto;
	padding: 10px;
	border-radius: 6px;
	background: rgba(0, 0, 0, 0.05);
	font-size: 12px;
	line-height: 1.4;
	white-space: pre;
}
</style>
