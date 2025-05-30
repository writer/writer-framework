import { Core, SourceFiles } from "@/writerTypes";
import { computed, ref, shallowRef, toRaw, watch } from "vue";
import {
	createFileToSourceFiles,
	deleteFileToSourceFiles,
	findSourceFileFromPath,
	getSourceFilesPathsToFiles,
	getSourceFilesPathsToNodes,
	isSourceFilesBinary,
	isSourceFilesDirectory,
	isSourceFilesFile,
} from "./sourceFiles";

export const SOURCE_FILE_MAX_SIZE_MB = 150;

export function useSourceFiles(wf: Core) {
	const sourceFileDraft = ref<SourceFiles>(
		structuredClone(toRaw(wf.sourceFiles.value)),
	);

	// synchronize `sourceFiles` & `sourceFileDraft`
	watch(wf.sourceFiles, (currentSourceFiles, previousSourceFiles) => {
		let wasUpdated = false;
		let tree = structuredClone(toRaw(sourceFileDraft.value));
		const pathsUnsavedStr =
			getDifferentPaths(previousSourceFiles).map(pathToStr);

		for (const path of getSourceFilesPathsToFiles(currentSourceFiles)) {
			const prev = findSourceFileFromPath(path, previousSourceFiles);

			const cur = findSourceFileFromPath(path, currentSourceFiles);
			if (isSourceFilesDirectory(cur)) continue;

			if (prev === undefined || isSourceFilesBinary(cur)) {
				// a file was added, we duplicate it to the draft
				tree = createFileToSourceFiles(
					path,
					tree,
					structuredClone(toRaw(cur)),
				);
				wasUpdated = true;
				continue;
			}

			if (!isSourceFilesFile(prev)) continue;

			const wasLoaded = !prev.complete && cur.complete;
			const hasBeenChanged = prev.complete && cur.complete;
			if (!wasLoaded && !hasBeenChanged) continue;

			const pathStr = pathToStr(path);
			if (pathsUnsavedStr.includes(pathStr)) continue;

			const draft = findSourceFileFromPath(path, tree);
			if (!isSourceFilesFile(draft)) continue;

			wasUpdated = true;
			draft.complete = true;
			draft.content = cur.content;
		}

		// handle deleted nodes
		for (const path of getSourceFilesPathsToNodes(tree)) {
			if (
				findSourceFileFromPath(path, currentSourceFiles) === undefined
			) {
				tree = deleteFileToSourceFiles(path, tree);
				wasUpdated = true;
			}
		}

		if (wasUpdated) sourceFileDraft.value = tree;
	});

	function pathToStr(path: string[]) {
		return path.join("/");
	}

	const filepathOpen = shallowRef<string[] | undefined>();

	const sourceFilesDraftPaths = computed(() =>
		Array.from(getSourceFilesPathsToFiles(sourceFileDraft.value)),
	);

	const pathsUnsaved = computed(() =>
		getDifferentPaths(wf.sourceFiles.value),
	);

	function getDifferentPaths(sourceFiles: SourceFiles) {
		return sourceFilesDraftPaths.value.filter((path) => {
			const draft = findSourceFileFromPath(path, sourceFileDraft.value);
			if (isSourceFilesBinary(draft)) return false;
			if (!isSourceFilesFile(draft)) return true;

			const file = findSourceFileFromPath(path, sourceFiles);
			if (!isSourceFilesFile(file)) return true;

			if (!draft.complete || !file.complete) return false;

			return draft.content !== file.content;
		});
	}

	const fileOpen = computed<SourceFiles | undefined>(() => {
		if (filepathOpen.value === undefined) return undefined;
		return findSourceFileFromPath(
			filepathOpen.value,
			sourceFileDraft.value,
		);
	});

	const code = computed({
		get() {
			return isSourceFilesFile(fileOpen.value)
				? fileOpen.value.content
				: "";
		},
		set(newCode: string) {
			if (filepathOpen.value === undefined) return;
			const node = findSourceFileFromPath(
				filepathOpen.value,
				sourceFileDraft.value,
			);
			if (!isSourceFilesFile(node)) return;
			node.content = newCode;
		},
	});

	function getNewFilename(i = 1): string {
		const filename = `new-file-${i}.txt`;

		return findSourceFileFromPath([filename], sourceFileDraft.value)
			? getNewFilename(i + 1)
			: filename;
	}

	async function openNewFile() {
		const newFile = getNewFilename();

		sourceFileDraft.value = createFileToSourceFiles(
			[newFile],
			toRaw(sourceFileDraft.value),
		);

		openFile([newFile]);

		await wf.sendCreateSourceFileRequest([newFile]);
	}

	const openedFileExtension = computed(() => {
		if (!filepathOpen.value?.length) return "";
		const filename = filepathOpen.value.at(-1);
		return filename.split(".").at(-1);
	});

	const openedFileLanguage = computed(() => {
		switch (openedFileExtension.value) {
			case "py":
				return "python";
			case "md":
			case "markdown":
				return "markdown";
			default:
				return openedFileExtension.value;
		}
	});

	function openFile(path: string[]) {
		filepathOpen.value = path;

		if (isSourceFilesFile(fileOpen.value) && !fileOpen.value.complete) {
			wf.requestSourceFileLoading(path);
		}
	}

	async function save(newPath?: string[]) {
		if (!filepathOpen.value || !fileOpen.value) return;

		if (fileOpen.value.type === "file") {
			await wf.sendCodeSaveRequest(code.value, filepathOpen.value);
		}

		if (newPath) {
			const oldPath = [...toRaw(filepathOpen.value)];
			filepathOpen.value = undefined;
			try {
				await wf.sendRenameSourceFileRequest(oldPath, newPath);
			} catch (e) {
				filepathOpen.value = oldPath;
				throw e;
			}
			openFile(newPath);
		}
	}

	function readFile(file: File): Promise<string | ArrayBuffer> {
		return new Promise((resolve, reject) => {
			const reader = new FileReader();
			reader.addEventListener("loadend", (event) => {
				const data = event.target.result;

				if (data instanceof ArrayBuffer) {
					const binaryString = String.fromCharCode.apply(
						null,
						new Uint8Array(data),
					);
					return resolve(binaryString);
				}

				resolve(data.split(",")[1]);
			});

			reader.addEventListener("error", () => {
				reject();
			});
			reader.readAsDataURL(file);
		});
	}

	async function upload(file: File) {
		const maxSizeBytes = SOURCE_FILE_MAX_SIZE_MB * 1024 * 1024;
		if (file.size > maxSizeBytes) {
			throw Error(
				`Cannot upload file bigger than ${SOURCE_FILE_MAX_SIZE_MB}mb`,
			);
		}

		const path = [file.name];

		if (findSourceFileFromPath(path, wf.sourceFiles.value))
			throw Error(`The file ${file.name} already exists`);

		sourceFileDraft.value = createFileToSourceFiles(
			path,
			toRaw(sourceFileDraft.value),
			{
				type: "binary",
				uploading: true,
			},
		);

		const content = await readFile(file);
		await wf.sendFileUploadRequest(path, content);
	}

	return {
		code,
		sourceFileDraft,
		fileOpen,
		filepathOpen,
		pathsUnsaved,
		openedFileLanguage,
		save,
		upload,
		openFile,
		openNewFile,
		getNewFilename,
	};
}
