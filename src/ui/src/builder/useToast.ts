import { readonly, shallowRef } from "vue";

export type ToastAction = { label: string; func: () => void; icon: string };

export type Toast = {
	id: number;
	type: "error" | "success" | "info";
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

	function pushToast(toast: Omit<Toast, "id">) {
		const id = new Date().getTime();
		toasts.value = [...toasts.value, { ...toast, id }];

		if (!toast.closable) {
			setTimeout(() => removeToast(id), toast.delayMs ?? 3_000);
		}
	}

	return {
		pushToast,
		removeToast,
		toasts: readonly(toasts),
	};
}
