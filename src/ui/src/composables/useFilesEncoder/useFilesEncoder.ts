import { MaybeRef, readonly, shallowRef, toValue } from "vue";
import { useAbortController } from "../useAbortController";
import { encodeFileAsDataURL, AbortError } from "./encodeFileAsDataURL";

export type UiFile = {
	id: string;
	name: string;
	size: number;
	file: File;
};

let fallbackId = 0;

function convertFileToUiFile(file: File): UiFile {
	const id = window.crypto?.randomUUID() ?? `file-${fallbackId++}`;

	return {
		id,
		file,
		name: file.name,
		size: file.size,
	};
}

export type EncodedFile = {
	name: string;
	type: string;
	data: string;
};

export type UseFilesEncoderParams = {
	multiple: MaybeRef<boolean>;
};

export function useFilesEncoder({ multiple }: UseFilesEncoderParams) {
	const abort = useAbortController();

	const uiFiles = shallowRef<UiFile[]>([]);

	function calcTotalSize(files: readonly Pick<File, "size">[]): number {
		return files.reduce((sum, file) => sum + file.size, 0);
	}

	function addFiles(files: File[]) {
		const convertedFiles = files.map((file) => convertFileToUiFile(file));

		uiFiles.value = toValue(multiple)
			? uiFiles.value.concat(convertedFiles)
			: convertedFiles.slice(0, 1);
	}

	function removeFile(id: string) {
		uiFiles.value = uiFiles.value.filter((uiFile) => uiFile.id !== id);
	}

	function replaceFiles(files: File[]) {
		const convertedFiles = files.map((file) => convertFileToUiFile(file));

		uiFiles.value = toValue(multiple)
			? convertedFiles
			: convertedFiles.slice(0, 1);
	}

	function clearFiles() {
		uiFiles.value = [];
	}

	async function encodeFiles(): Promise<{
		encodedFiles: EncodedFile[];
		rejectedFiles: Error[];
	}> {
		const settledResults = await Promise.allSettled(
			uiFiles.value.map(async ({ file }) => {
				const encodedFile = await encodeFileAsDataURL(file, {
					signal: abort.signal,
				});

				return {
					name: file.name,
					type: file.type,
					data: encodedFile,
				};
			}),
		);

		const encodedFiles: EncodedFile[] = [];
		const rejectedFiles: Error[] = [];

		settledResults.forEach((result) => {
			if (result.status === "fulfilled") {
				encodedFiles.push(result.value);
			} else if (result.reason instanceof Error) {
				if (result.reason instanceof AbortError) {
					// skip aborted files from the results
					return;
				}

				rejectedFiles.push(result.reason);
			}
		});

		return {
			encodedFiles,
			rejectedFiles,
		};
	}

	return {
		files: readonly(uiFiles),

		calcTotalSize,

		addFiles,
		removeFile,
		replaceFiles,
		clearFiles,

		encodeFiles,
	};
}
