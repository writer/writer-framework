import { onMounted, onUnmounted } from "vue";

interface KeyboardShortcut {
	key: string;
	modifier?: 'ctrl' | 'cmd' | 'alt' | 'shift';
	handler: () => void;
	preventDefault?: boolean;
}

export function useKeyboardShortcuts(shortcuts: KeyboardShortcut[]) {
	let abortController: AbortController | null = null;

	function isModifierActive(event: KeyboardEvent, modifier?: string): boolean {
		switch (modifier) {
			case 'ctrl':
				return event.ctrlKey && !event.metaKey;
			case 'cmd':
				return event.metaKey && !event.ctrlKey;
			case 'alt':
				return event.altKey;
			case 'shift':
				return event.shiftKey;
			default:
				return true;
		}
	}

	function handleKeydown(event: KeyboardEvent) {
		for (const shortcut of shortcuts) {
			const keyMatches = event.key.toLowerCase() === shortcut.key.toLowerCase();
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
		abortController = new AbortController();
		document.addEventListener("keydown", handleKeydown, {
			signal: abortController.signal,
		});
	});

	onUnmounted(() => {
		if (abortController) {
			abortController.abort();
		}
	});
}

