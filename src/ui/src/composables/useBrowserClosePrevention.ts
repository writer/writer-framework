import { ref, onMounted } from "vue";

export function useBrowserClosePrevention() {
	const shouldPreventClose = ref(false);

	function handleBeforeUnload(event: BeforeUnloadEvent) {
		if (shouldPreventClose.value) {
			event.preventDefault();
			event.returnValue = "";
			return "";
		}
	}

	function enableClosePrevention() {
		shouldPreventClose.value = true;
	}

	window.addEventListener("beforeunload", handleBeforeUnload);

	onMounted(() => {
		return () => {
			window.removeEventListener("beforeunload", handleBeforeUnload);
		};
	});

	return {
		shouldPreventClose,
		enableClosePrevention,
	};
}
