export function dataUrlToBase64(url: string) {
	const base64 = url.split(",")?.[1];
	if (!base64) throw Error(`Could not extract base64 from data url: ${url}`);
	return base64;
}

export function base64ToArrayBuffer(base64: string) {
	const binaryString = window.atob(base64);
	const len = binaryString.length;
	const bytes = new Uint8Array(len);
	for (let i = 0; i < len; i++) {
		bytes[i] = binaryString.charCodeAt(i);
	}
	return bytes.buffer;
}

export function dataURLToArrayBuffer(dataURL: string) {
	const base64String = dataUrlToBase64(dataURL);
	const binaryString = atob(base64String);

	const buffer = new ArrayBuffer(binaryString.length);
	const bytes = new Uint8Array(buffer);

	for (let i = 0; i < binaryString.length; i++) {
		bytes[i] = binaryString.charCodeAt(i);
	}

	return buffer;
}
