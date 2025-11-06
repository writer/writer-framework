import { ref, onMounted, onUnmounted } from "vue";
import { useAbortController } from "@/composables/useAbortController";
import { SocketTimeout } from "@/writerTypes";

const BEFORE_UNLOAD_MESSAGE =
	"You have unsaved changes. Are you sure you want to leave?";

export function useUnsavedChangesPrevention(socketTimeout?: SocketTimeout) {
	const hasUnsavedChanges = ref(false);
	const beforeUnloadHandler = ref<
		((event: BeforeUnloadEvent) => void) | null
	>(null);

	function enablePrevention() {
		hasUnsavedChanges.value = true;
		if (socketTimeout) socketTimeout.prevent.value = true;
	}

	function disablePrevention() {
		hasUnsavedChanges.value = false;
		if (socketTimeout) socketTimeout.prevent.value = false;
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
			window.removeEventListener(
				"beforeunload",
				beforeUnloadHandler.value,
			);
		}
	});

	const abort = useAbortController();
	onMounted(() => {
		window.addEventListener("beforeunload", handleBeforeUnload, {
			signal: abort.signal,
		});
	});

	return {
		enablePrevention,
		disablePrevention,
	};
}
