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
