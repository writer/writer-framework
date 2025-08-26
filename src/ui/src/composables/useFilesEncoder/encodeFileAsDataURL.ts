export class AbortError extends Error {
	constructor(message: string = "Operation aborted") {
		super(message);
		this.name = AbortError.name;
	}
}

export type EncodeFileAsDataURLParams = {
	onProgress?: (percent: number, loaded: number, total: number) => void;
	signal?: AbortSignal;
};

export function encodeFileAsDataURL(
	file: File,
	{ onProgress, signal }: EncodeFileAsDataURLParams = {},
): Promise<string> {
	const reader = new FileReader();

	return new Promise<string>((resolve, reject) => {
		reader.onload = () => {
			resolve(String(reader.result) || "");
		};

		reader.onerror = () => {
			reject(reader.error ?? new Error("Failed to read file"));
		};

		reader.onprogress = ({ lengthComputable, loaded, total }) => {
			if (typeof onProgress === "function" && lengthComputable) {
				const percent = Math.round((loaded / total) * 100);

				onProgress(percent, loaded, total);
			}
		};

		reader.onabort = () => {
			reject(new AbortError());
		};

		if (signal instanceof AbortSignal) {
			if (signal.aborted) {
				reader.abort();

				return;
			}

			signal.addEventListener("abort", () => reader.abort(), {
				once: true,
			});
		}

		reader.readAsDataURL(file);
	});
}
