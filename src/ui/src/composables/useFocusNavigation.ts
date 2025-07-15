import type { Ref } from "vue";

/**
 * Will try to focus the next button in the `element` using the arrow keys
 */
export function useFocusNavigation(
	element: Ref<HTMLElement>,
	callbacks?: { nextFocusNotFound?: () => void },
) {
	return function onKeydown(e: KeyboardEvent) {
		if (!element.value) return;

		let direction = 0;
		if (e.key === "ArrowDown") {
			direction = 1;
		} else if (e.key === "ArrowUp") {
			direction = -1;
		}

		if (direction === 0) return;

		const options = Array.from(
			element.value.querySelectorAll("button"),
		).filter(
			(el) => !el.hasAttribute("disabled") && el.offsetParent !== null,
		);

		let focusEl = direction === 1 ? options[0] : options.at(-1);

		const focusedIndex = options.indexOf(
			document.activeElement as HTMLButtonElement,
		);

		if (focusedIndex !== -1) {
			focusEl = options[focusedIndex + direction];
		}

		if (focusEl) {
			focusEl.focus();
			e.preventDefault();
		} else {
			callbacks?.nextFocusNotFound?.();
		}
	};
}
