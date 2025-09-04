import { computed, DeepReadonly, MaybeRef, toValue } from "vue";
import accept from "attr-accept";

export type UseFileTypeAcceptParams = {
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
				// '*.pdf' -> '.pdf'
				result.add(
					normalizedType.startsWith("*.")
						? normalizedType.slice(1)
						: normalizedType,
				);
			}
		});

		return [...result];
	});

	const acceptAttr = computed<string | undefined>(
		() => normalizedAcceptedFileTypes.value.join(",") || undefined,
	);

	function checkIsFileAccepted(file: File): boolean {
		return accept(file, normalizedAcceptedFileTypes.value);
	}

	return {
		acceptAttr,
		checkIsFileAccepted,
	};
}
