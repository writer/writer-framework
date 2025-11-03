import { onMounted } from "vue";
import { useAbortController } from "../../composables/useAbortController";

export interface KeyboardShortcut {
	key: string;
	modifier?: "ctrl" | "cmd" | "alt" | "shift";
	handler: () => void;
	preventDefault?: boolean;
}

export function useKeyboardShortcuts(shortcuts: KeyboardShortcut[]) {
	const abortController = useAbortController();

	function isModifierActive(
		event: KeyboardEvent,
		modifier?: string,
	): boolean {
		switch (modifier) {
			case "ctrl":
				return event.ctrlKey && !event.metaKey;
			case "cmd":
				return event.metaKey && !event.ctrlKey;
			case "alt":
				return event.altKey;
			case "shift":
				return event.shiftKey;
			default:
				return (
					!event.ctrlKey &&
					!event.metaKey &&
					!event.altKey &&
					!event.shiftKey
				);
		}
	}

	function handleKeydown(event: KeyboardEvent) {
		for (const shortcut of shortcuts) {
			const keyMatches =
				event.key.toLowerCase() === shortcut.key.toLowerCase();
			const modifierMatches = isModifierActive(event, shortcut.modifier);

			if (keyMatches && modifierMatches) {
				if (shortcut.preventDefault !== false) {
					event.preventDefault();
				}
				shortcut.handler();
				return;
			}
		}
	}

	onMounted(() => {
		document.addEventListener("keydown", handleKeydown, {
			signal: abortController.signal,
		});
	});
}
