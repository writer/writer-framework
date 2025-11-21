export function readBlobAsArrayBuffer(blob: Blob): Promise<ArrayBuffer | null> {
	return new Promise((res, rej) => {
		const reader = new FileReader();
		reader.onload = () => {
			res(reader.result as ArrayBuffer | null);
		};
		reader.onerror = (error) => {
			rej(error);
		};
		reader.readAsArrayBuffer(blob);
	});
}

export async function readBlobAsArrayBufferJson<T>(
	blob: Blob,
): Promise<T | undefined> {
	const buffer = await readBlobAsArrayBuffer(blob);

	if (!buffer) return undefined;
	const decoder = new TextDecoder("utf-8");
	return JSON.parse(decoder.decode(buffer));
}

/**
 * Downloads a blob as a file with the specified filename
 */
export function downloadBlob(blob: Blob, filename: string): void {
	const url = URL.createObjectURL(blob);
	try {
		const a = document.createElement("a");
		a.href = url;
		a.download = filename;
		document.body.appendChild(a);
		a.click();
		document.body.removeChild(a);
	} finally {
		URL.revokeObjectURL(url);
	}
}

/**
 * Downloads an object as a JSON file
 */
export function downloadJson(data: unknown, filename: string): void {
	const jsonString = JSON.stringify(data, null, 2);
	const blob = new Blob([jsonString], { type: "application/json" });
	downloadBlob(blob, filename);
}
