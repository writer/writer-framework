import { ref } from "vue";

interface PendingAction {
	action: () => void;
	description?: string;
}

export function useUnsavedChangesModal() {
	const showModal = ref(false);
	const pendingAction = ref<PendingAction | null>(null);

	const showUnsavedChangesModal = (action: () => void, description?: string) => {
		showModal.value = true;
		pendingAction.value = { action, description };
	};

	const executePendingAction = () => {
		if (pendingAction.value) {
			pendingAction.value.action();
			pendingAction.value = null;
		}
		showModal.value = false;
	};

	const cancelPendingAction = () => {
		pendingAction.value = null;
		showModal.value = false;
	};

	const checkUnsavedChanges = (
		hasUnsavedChanges: boolean,
		action: () => void,
		description?: string,
	): boolean => {
		if (hasUnsavedChanges) {
			showUnsavedChangesModal(action, description);
			return true;
		}
		return false;
	};

	return {
		showModal,
		executePendingAction,
		cancelPendingAction,
		checkUnsavedChanges,
	};
}

