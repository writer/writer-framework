import { Core, SourceFiles } from "@/writerTypes";
import { computed, ref, shallowRef, toRaw, watch } from "vue";
import {
	createFileToSourceFiles,
	deleteFileToSourceFiles,
	findSourceFileFromPath,
	getSourceFilesPathsToFiles,
	getSourceFilesPathsToNodes,
	isSourceFilesBinary,
	isSourceFilesFile,
} from "./sourceFiles";

export function useSourceFiles(wf: Core) {
	const sourceFileDraft = ref<SourceFiles>(
		structuredClone(toRaw(wf.sourceFiles.value)),
	);

	// synchronize `sourceFiles` & `sourceFileDraft`
	watch(wf.sourceFiles, (currentSourceFiles, previousSourceFiles) => {
		let wasUpdated = false;
		let tree = structuredClone(toRaw(sourceFileDraft.value));

		for (const path of getSourceFilesPathsToFiles(currentSourceFiles)) {
			const prev = findSourceFileFromPath(path, previousSourceFiles);

			const cur = findSourceFileFromPath(path, currentSourceFiles);
			if (!isSourceFilesFile(cur)) continue;

			if (prev === undefined) {
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
			if (!wasLoaded) continue;

			//  change because an element is loaded, we update the draft
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

	const filepathOpen = shallowRef<string[] | undefined>();

	const sourceFilesDraftPaths = computed(() =>
		Array.from(getSourceFilesPathsToFiles(sourceFileDraft.value)),
	);

	const pathsUnsaved = computed(() => {
		return sourceFilesDraftPaths.value.filter((path) => {
			const draft = findSourceFileFromPath(path, sourceFileDraft.value);
			if (isSourceFilesBinary(draft)) return false;
			if (!isSourceFilesFile(draft)) return true;

			const file = findSourceFileFromPath(path, wf.sourceFiles.value);
			if (!isSourceFilesFile(file)) return true;

			if (!draft.complete || !file.complete) return false;

			return draft.content !== file.content;
		});
	});

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

				resolve(data);
			});

			reader.addEventListener("error", () => {
				reject();
			});
			reader.readAsArrayBuffer(file);
		});
	}

	async function upload(files: FileList) {
		const maxSize = 100 * 1024 * 1024; // 100mb
		for (const file of files) {
			if (file.size > maxSize)
				throw Error("Cannot upload file bigger than 100mb");

			const path = [file.name];

			if (findSourceFileFromPath(path, wf.sourceFiles.value))
				throw Error(`The file ${file.name} already exists`);

			const content = await readFile(file);
			// TODO: validate size here
			await wf.sendFileUploadRequest(path, content);
		}
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
