<template>
	<BuilderPanel
		panel-id="code"
		name="Code"
		:contents-teleport-el="contentsTeleportEl"
		:actions="[]"
		:scrollable="false"
		enable-left-panel
		keyboard-shortcut-key="J"
		class="BuilderCodePanel"
		enable-drop-file
		@files-drop="handleUpload"
		@openned="onOpenPanel"
	>
		<template #leftPanel>
			<div class="BuilderCodePanel__tree">
				<BuilderCodePanelSourceFilesTree
					:path-active="filepathOpen"
					:paths-unsaved="pathsUnsaved"
					:source-files="sourceFileDraft"
					@add-file="handleAddFile"
					@select="openFile"
					@delete="handleDeleteFile"
				/>
				<div class="BuilderCodePanel__tree__actions">
					<WdsButtonLink
						left-icon="add"
						text="Add file"
						@click="handleAddFile"
					/>
					<BuilderCodePanelFileUploadBtn @selected="handleUpload" />
				</div>
			</div>
		</template>
		<BuilderEmbeddedCodeEditor
			v-if="fileTypeOpen === 'file'"
			v-model="code"
			variant="full"
			:language="openedFileLanguage"
			:disabled="isDisabled"
		/>
		<div
			v-if="fileTypeOpen === 'binary'"
			class="BuilderCodePanel__noPreview"
		>
			<img
				class="BuilderCodePanel__noPreview__img"
				src="@/assets/art-paper.svg"
			/>
			<p class="BuilderCodePanel__noPreview__title">Can’t Preview File</p>
			<p class="BuilderCodePanel__noPreview__desc">
				Non-text files are not available to view here
			</p>
		</div>
		<template #actionsCompanion>
			<div class="BuilderCodePanel__actionsCompanion">
				<WdsTextInput
					ref="filenameEl"
					v-model="filename"
					:disabled="!isRenaminAllowed"
					class="BuilderCodePanel__actionsCompanion__filename"
					autofocus
					variant="ghost"
					@keydown.enter="handleSave"
				/>
				<WdsButton
					variant="primary"
					size="small"
					:disabled="isDisabled || isCodeSaved"
					class="BuilderCodePanel__actionsCompanion__saveBtn"
					@click="handleSave"
				>
					<i class="material-symbols-outlined">keyboard_backspace</i>
					Save file
				</WdsButton>
				<SharedMoreDropdown
					:disabled="moreOptionsDisabled"
					:options="moreOptions"
					@select="handleMoreSelect"
				/>
			</div>
		</template>
	</BuilderPanel>
</template>

<script setup lang="ts">
import {
	computed,
	defineAsyncComponent,
	inject,
	nextTick,
	onMounted,
	onUnmounted,
	ref,
	useTemplateRef,
	watch,
} from "vue";
import BuilderPanel from "./BuilderPanel.vue";
import BuilderAsyncLoader from "../BuilderAsyncLoader.vue";
import injectionKeys from "@/injectionKeys";
import { useSourceFiles } from "@/core/useSourceFiles";
import WdsTextInput from "@/wds/WdsTextInput.vue";
import WdsButton from "@/wds/WdsButton.vue";
import type { Option } from "@/components/shared/SharedMoreDropdown.vue";
import BuilderCodePanelSourceFilesTree from "./BuilderCodePanelSourceFilesTree.vue";
import { useToasts } from "../useToast";
import { useLogger } from "@/composables/useLogger";
import BuilderCodePanelFileUploadBtn from "./BuilderCodePanelFileUploadBtn.vue";
import WdsButtonLink from "@/wds/WdsButtonLink.vue";

const SharedMoreDropdown = defineAsyncComponent(
	() => import("@/components/shared/SharedMoreDropdown.vue"),
);

const BuilderEmbeddedCodeEditor = defineAsyncComponent({
	loader: () => import("../BuilderEmbeddedCodeEditor.vue"),
	loadingComponent: BuilderAsyncLoader,
});

defineProps<{
	contentsTeleportEl: HTMLElement;
}>();

const wf = inject(injectionKeys.core);

const moreOptions: Option[] = [
	{ label: "Rename file", value: "rename", icon: "edit" },
	{ label: "Delete file", value: "delete", icon: "delete" },
];

const {
	sourceFileDraft,
	openFile,
	upload,
	openNewFile,
	code,
	openedFileLanguage,
	filepathOpen,
	fileOpen,
	pathsUnsaved,
	save,
} = useSourceFiles(wf);

async function handleUpload(files: FileList | File[]) {
	await Promise.all([...files].map(handleFileUpload));
}
async function handleFileUpload(file: File) {
	try {
		await upload(file);
		pushToast({
			type: "success",
			message: `File ${file.name} uploaded`,
		});
	} catch (error) {
		pushToast({ type: "error", message: error.message });
	}
}

const fileTypeOpen = computed(() => fileOpen.value?.type);

const { pushToast } = useToasts();

const logger = useLogger();

function useKeydownCmdS(callback: () => void | Promise<void>) {
	const abortController = new AbortController();
	onMounted(() => {
		document.addEventListener(
			"keydown",
			async (event) => {
				const isCmdOrCtrl = event.metaKey || event.ctrlKey;
				const isSKey = event.key === "s" || event.key === "S";
				if (!isCmdOrCtrl || !isSKey) return;

				event.preventDefault(); // Prevent the default save dialog
				await callback();
			},
			{ signal: abortController.signal },
		);
	});
	onUnmounted(abortController.abort);
}
useKeydownCmdS(handleSave);

const filenameEl = useTemplateRef("filenameEl");
const filename = ref("");
const isDisabled = ref(false);

const filepathOpenStr = computed(() => filepathOpen.value?.join("/") ?? "");
const isRenaminAllowed = computed(() => filepathOpenStr.value !== "main.py");
const isRenaming = computed(() => filepathOpenStr.value !== filename.value);

const moreOptionsDisabled = computed(
	() => isDisabled.value || filepathOpenStr.value === "main.py",
);

const isCodeSaved = computed(() => {
	if (isRenaming.value) return false;
	if (filepathOpen.value === undefined) return true;

	return !pathsUnsaved.value
		.map((p) => p.join("/"))
		.includes(filepathOpenStr.value);
});

watch(filepathOpen, () => {
	filename.value = filepathOpen.value?.join("/") ?? "";
});

watch(wf.sessionTimestamp, () => {
	isDisabled.value = false;
});

function onOpenPanel(open: boolean) {
	if (!open) return;
	if (filepathOpen.value === undefined) openFile(["main.py"]);
}

async function openRenameMode() {
	if (filepathOpenStr.value === "main.py") return;
	await nextTick();
	filenameEl.value?.focus();
}

async function handleMoreSelect(key: string) {
	switch (key) {
		case "rename":
			return openRenameMode();
		case "delete":
			await handleDeleteFile(filepathOpen.value);
	}
}

async function handleAddFile() {
	await openNewFile();
	openRenameMode();
}

async function handleDeleteFile(path: string[]) {
	await wf.sendDeleteSourceFileRequest(path);
	pushToast({ type: "success", message: "The file was deleted" });

	const currentFileDeleted = filepathOpen.value
		.join("/")
		.startsWith(path.join("/"));

	if (currentFileDeleted) openFile(["main.py"]);
}

async function handleSave() {
	if (filepathOpen.value === undefined) {
		return pushToast({ type: "error", message: "There is no file open" });
	} else if (isCodeSaved.value) {
		return pushToast({
			type: "info",
			message: "There are not file changes to save",
		});
	}

	isDisabled.value = true;

	try {
		await save(isRenaming.value ? filename.value.split("/") : undefined);
		pushToast({ type: "success", message: "The file was saved" });
	} catch (error) {
		logger.error("The file hasn't been saved.", error);
		pushToast({ type: "error", message: "The file hasn't been saved" });
		return;
	} finally {
		isDisabled.value = false;
	}
}
</script>

<style scoped>
.BuilderCodePanel__tree {
	height: 100%;
	width: 100%;
	padding: 4px;
	overflow-y: auto;
}

.BuilderCodePanel__tree__actions {
	display: flex;
	justify-content: space-between;
	flex-wrap: wrap;
	padding: 8px;
	padding-left: 12px;
}

.BuilderCodePanel__actionsCompanion {
	width: 100%;
	display: flex;
	gap: 12px;
	align-items: center;
	justify-content: right;
}

.BuilderCodePanel__actionsCompanion__filename {
	height: 32px;
	flex-grow: 1;
}

.BuilderCodePanel__actionsCompanion__saveBtn {
	min-width: 120px;
}

.BuilderCodePanel__noPreview {
	display: flex;
	flex-direction: column;
	font-size: 14px;
	height: 100%;
	width: 100%;
	justify-content: center;
	align-items: center;
}

.BuilderCodePanel__noPreview__img {
	height: 170px;
	margin-bottom: 32px;
}

.BuilderCodePanel__noPreview__title {
	font-size: 16px;
	margin-bottom: 2px;
}

.BuilderCodePanel__noPreview__desc {
	color: var(--wdsColorGray6);
	font-size: 12px;
}
</style>
