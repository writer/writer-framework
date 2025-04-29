import { useLogger } from "@/composables/useLogger";
import { Component } from "@/writerTypes";

type ClipboardData = {
	type: "writer/clipboard";
	components: Component[];
};

function isClipboardData(data: unknown): data is ClipboardData {
	return (
		typeof data === "object" &&
		data !== null &&
		"type" in data &&
		data.type === "writer/clipboard" &&
		"components" in data &&
		Array.isArray(data.components)
	);
}

export function useComponentClipboard() {
	const logger = useLogger();

	async function get(): Promise<Component[] | undefined> {
		try {
			const text = await navigator.clipboard.readText();
			const data = JSON.parse(text);
			return isClipboardData(data) ? data.components : undefined;
		} catch {
			return undefined;
		}
	}

	function set(value: Component[]) {
		const data: ClipboardData = {
			type: "writer/clipboard",
			components: value,
		};
		try {
			navigator.clipboard.writeText(JSON.stringify(data));
		} catch (e) {
			logger.warn("Failed to write components in the clipboard", e);
		}
	}

	return { get, set };
}
