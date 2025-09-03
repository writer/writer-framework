import { readonly, shallowRef } from "vue";

export type ToastAction = { label: string; func: () => void; icon: string };

export type Toast = {
	id: number;
	type: "error" | "success" | "info" | "loading";
	message: string;
	closable?: boolean;
	delayMs?: number;
	action?: ToastAction;
};

const toasts = shallowRef<Toast[]>([]);

export function useToasts() {
	function removeToast(id: number) {
		toasts.value = toasts.value.filter((t) => t.id !== id);
	}

	function pscheduleClosing(toast: Toast) {
		if (!toast.closable && toast.delayMs !== Infinity) {
			setTimeout(() => removeToast(toast.id), toast.delayMs ?? 3_000);
		}
	}

	function pushToast(toastData: Omit<Toast, "id">) {
		const id = new Date().getTime();
		const toast: Toast = { ...toastData, id };
		toasts.value = [...toasts.value, toast];
		pscheduleClosing(toast);

		return id;
	}

	function updateToast(toast: Toast) {
		toasts.value = toasts.value.map((t) => (t.id === toast.id ? toast : t));
		pscheduleClosing(toast);
	}

	return {
		pushToast,
		removeToast,
		updateToast,
		toasts: readonly(toasts),
	};
}
