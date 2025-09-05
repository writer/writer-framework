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
	const scheduleClosingTimers: Record<
		Toast["id"],
		ReturnType<typeof setTimeout>
	> = {};

	function removeToast(id: number) {
		const toastIndex = toasts.value.findIndex((t) => t.id === id);
		if (toastIndex === -1) return;
		toasts.value = toasts.value.filter((_, i) => toastIndex !== i);
	}

	function scheduleClosing(toast: Toast) {
		if (scheduleClosingTimers[toast.id]) {
			clearTimeout(scheduleClosingTimers[toast.id]);
			delete scheduleClosingTimers[toast.id];
		}

		if (!toast.closable && toast.delayMs !== Infinity) {
			scheduleClosingTimers[toast.id] = setTimeout(
				() => removeToast(toast.id),
				toast.delayMs ?? 3_000,
			);
		}
	}

	function pushToast(toastData: Omit<Toast, "id"> | Toast) {
		if (
			"id" in toastData &&
			toasts.value.some((t) => t.id === toastData.id)
		) {
			toasts.value = toasts.value.map((t) =>
				t.id === toastData.id ? toastData : t,
			);
			scheduleClosing(toastData);
			return toastData.id;
		}

		const id = "id" in toastData ? toastData.id : new Date().getTime();
		const toast: Toast = { ...toastData, id };
		toasts.value = [...toasts.value, toast];
		scheduleClosing(toast);

		return id;
	}

	return {
		pushToast,
		removeToast,
		toasts: readonly(toasts),
	};
}
