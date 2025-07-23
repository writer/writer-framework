import { ref, shallowRef } from "vue";

export function useHistoryStack<T>() {
	const stack = shallowRef<T[]>([]);

	const index = ref(-1);

	function push(value: T) {
		stack.value = [...stack.value.slice(0, index.value + 1), value];
		index.value = stack.value.length - 1;
	}

	function undo(): T | undefined {
		if (index.value <= 0) return;
		index.value -= 1;
		return get();
	}

	function redo(): T | undefined {
		if (index.value < 0) return;
		index.value += 1;
		return get();
	}

	function get(): T | undefined {
		if (index.value < 0 || index.value >= stack.value.length) return;

		return stack.value[index.value];
	}

	return { push, undo, redo };
}
