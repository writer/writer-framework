export function useDebouncer(callback: () => void | Promise<void>, ms: number) {
	let id: ReturnType<typeof setTimeout>;
	return () => {
		if (id) clearTimeout(id);
		id = setTimeout(callback, ms);
	};
}
