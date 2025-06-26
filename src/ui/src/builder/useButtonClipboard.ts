import { MaybeRef, ref, unref } from "vue";

export function useButtonClipboard(text: MaybeRef<string>) {
	const isCopied = ref(false);

	async function copyText() {
		if (!navigator.clipboard) {
			throw new Error("Clipboard API not supported");
		}

		await navigator.clipboard.writeText(unref(text));

		isCopied.value = true;
		setTimeout(() => (isCopied.value = false), 1000);
	}

	return { copyText, isCopied };
}
