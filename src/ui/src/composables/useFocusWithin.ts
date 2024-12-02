import { ComputedRef, onBeforeUnmount, readonly, Ref, ref, watch } from "vue";

/**
 * Detect if a given element or its children has focus.
 * Inspired from <https://danburzo.ro/focus-within>.
 */
export function useFocusWithin(
	element: ComputedRef<HTMLElement> | Ref<HTMLElement>,
) {
	const focus = ref(false);

	function onFocusIn() {
		focus.value = true;
	}

	function onFocusOut(e: FocusEvent) {
		const target = e.currentTarget as HTMLElement;
		// If the document has lost focus, don't hide the container just yet, wait until the focus is returned.
		if (!document.hasFocus()) {
			window.addEventListener("focus", function focusReturn() {
				// We want the listener to be triggered just once, so we have it remove itself from the `focus` event.
				window.removeEventListener("focus", focusReturn);

				// Test whether the container is still in the DOM and whether the active element is contained within.
				if (
					target.isConnected &&
					!target.contains(document.activeElement)
				) {
					focus.value = false;
				}
			});
		} else if (!target.contains(e.relatedTarget as HTMLElement)) {
			focus.value = false;
		}
	}

	watch(element, (_, previous) => {
		if (previous) {
			previous.removeEventListener("focusin", onFocusIn);
			previous.removeEventListener("focusout", onFocusOut);
		}

		if (!element) return;

		element.value.addEventListener("focusin", onFocusIn);
		element.value.addEventListener("focusout", onFocusOut);
	});

	onBeforeUnmount(() => {
		element.value.removeEventListener("focusin", onFocusIn);
		element.value.removeEventListener("focusout", onFocusOut);
	});

	return readonly(focus);
}
