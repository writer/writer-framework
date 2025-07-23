export function useDebouncer<ARGS extends unknown[]>(
	callback: (...args: ARGS) => void | Promise<void>,
	ms: number,
) {
	let id: ReturnType<typeof setTimeout>;
	return (...args: ARGS) => {
		if (id) clearTimeout(id);
		id = setTimeout(() => callback(...args), ms);
	};
}
