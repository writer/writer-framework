import { useLogger } from "@/composables/useLogger";
import { Component } from "@/writerTypes";
import { computed, onMounted, onUnmounted, shallowRef } from "vue";

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

let intervalId: ReturnType<typeof setInterval> | undefined;

export function useComponentClipboard() {
	const components = shallowRef<Component[]>([]);
	const logger = useLogger();

	onMounted(async () => {
		components.value = await get();

		if (intervalId) return;

		intervalId = setInterval(async () => {
			components.value = await get();
		}, 1_000);
	});

	onUnmounted(() => {
		if (intervalId) clearInterval(intervalId);
	});

	async function get(): Promise<Component[]> {
		try {
			const text = await navigator.clipboard.readText();
			const data = JSON.parse(text);
			return isClipboardData(data) ? data.components : [];
		} catch {
			return [];
		}
	}

	return computed<Component[]>({
		get() {
			return components.value;
		},
		set(value) {
			components.value = value;
			try {
				const data: ClipboardData = {
					type: "writer/clipboard",
					components: value,
				};
				navigator.clipboard.writeText(JSON.stringify(data));
			} catch (e) {
				logger.warn("Failed to write components in the clipboard", e);
			}
		},
	});
}
