import { MaybeRef, readonly, ref, toValue } from "vue";
import { encodeFileAsDataURL } from "./encodeFileAsDataURL";

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
	const uiFiles = ref<UiFile[]>([]);
	const isEncoding = ref(false);

	function calcTotalSize(files: readonly Pick<File, "size">[]): number {
		return files.reduce((sum, file) => sum + file.size, 0);
	}

	function addFiles(files: File[]) {
		if (toValue(multiple)) {
			uiFiles.value = uiFiles.value.concat(
				files.map((file) => convertFileToUiFile(file)),
			);
		} else {
			uiFiles.value = files.map((file) => convertFileToUiFile(file));
		}
	}

	function removeFile(id: string) {
		const index = uiFiles.value.findIndex((uiFile) => uiFile.id === id);

		if (index !== -1) {
			uiFiles.value.splice(index, 1);
		}
	}

	function replaceFiles(files: File[]) {
		uiFiles.value = files.map((file) => convertFileToUiFile(file));
	}

	function clearFiles() {
		uiFiles.value = [];
	}

	async function encodeFiles(): Promise<{
		encodedFiles: EncodedFile[];
		rejectedFiles: Error[];
	}> {
		if (uiFiles.value.length === 0) {
			return;
		}

		if (isEncoding.value) {
			return;
		}

		isEncoding.value = true;

		const settledResults = await Promise.allSettled(
			uiFiles.value.map(async ({ file }) => {
				const encodedFile = await encodeFileAsDataURL(file);

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
				rejectedFiles.push(result.reason);
			}
		});

		isEncoding.value = false;

		return {
			encodedFiles,
			rejectedFiles,
		};
	}

	return {
		files: readonly(uiFiles),
		isEncoding: readonly(isEncoding),

		calcTotalSize,

		addFiles,
		removeFile,
		replaceFiles,
		clearFiles,

		encodeFiles,
	};
}
