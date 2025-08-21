import { computed, DeepReadonly, MaybeRef, toValue } from "vue";

type UseFileTypeAcceptParams = {
	acceptedFileTypes?: DeepReadonly<MaybeRef<string[]>>;
};

export function useFileTypeAccept({
	acceptedFileTypes = [],
}: UseFileTypeAcceptParams) {
	const normalizedAcceptedFileTypes = computed<string[]>(() => {
		const fileTypes = toValue(acceptedFileTypes);

		if (!Array.isArray(fileTypes) || fileTypes.length === 0) {
			return [];
		}

		const result = new Set<string>();

		fileTypes.forEach((fileType) => {
			if (typeof fileType !== "string") {
				return;
			}

			const normalizedType = fileType.trim().toLowerCase();

			if (normalizedType) {
				result.add(normalizedType);
			}
		});

		return [...result];
	});

	const acceptAttr = computed<string | undefined>(
		() => normalizedAcceptedFileTypes.value.join(", ") || undefined,
	);

	const matchers = computed(() => {
		const extensions = new Set<string>();
		const wildcards = new Set<string>();
		const mimes = new Set<string>();

		normalizedAcceptedFileTypes.value.forEach((fileType) => {
			if (fileType.startsWith(".")) {
				extensions.add(fileType);
			} else if (fileType.endsWith("/*")) {
				// 'image/*' -> 'image/'
				wildcards.add(fileType.slice(0, -1));
			} else {
				mimes.add(fileType);
			}
		});

		return {
			extensions,
			wildcards: [...wildcards],
			mimes,
		};
	});

	function checkIsFileAccepted(file: File): boolean {
		if (normalizedAcceptedFileTypes.value.length === 0) {
			// no restrictions, all files are accepted
			return true;
		}

		const fileType = (file.type || "").toLowerCase();
		const fileName = (file.name || "").toLowerCase();

		const dotIndex = fileName.lastIndexOf(".");
		const fileExtension = dotIndex > -1 ? fileName.slice(dotIndex) : "";

		return (
			matchers.value.mimes.has(fileType) ||
			matchers.value.wildcards.some((p) => fileType.startsWith(p)) ||
			matchers.value.extensions.has(fileExtension)
		);
	}

	return {
		normalizedAcceptedFileTypes,
		acceptAttr,
		checkIsFileAccepted,
	};
}
