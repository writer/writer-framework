import { ref, onMounted, onUnmounted } from "vue";

const BEFORE_UNLOAD_MESSAGE = "You have unsaved changes. Are you sure you want to leave?";

export function useUnsavedChangesPrevention() {
	const hasUnsavedChanges = ref(false);
	const beforeUnloadHandler = ref<((event: BeforeUnloadEvent) => void) | null>(null);

	function enablePrevention() {
		hasUnsavedChanges.value = true;
	}

	function disablePrevention() {
		hasUnsavedChanges.value = false;
	}

	function handleBeforeUnload(event: BeforeUnloadEvent) {
		if (hasUnsavedChanges.value) {
			event.preventDefault();
			event.returnValue = BEFORE_UNLOAD_MESSAGE;
			return BEFORE_UNLOAD_MESSAGE;
		}
	}

	onMounted(() => {
		beforeUnloadHandler.value = handleBeforeUnload;
		window.addEventListener("beforeunload", beforeUnloadHandler.value);
	});

	onUnmounted(() => {
		if (beforeUnloadHandler.value) {
			window.removeEventListener("beforeunload", beforeUnloadHandler.value);
		}
	});

	return {
		enablePrevention,
		disablePrevention,
	};
}

