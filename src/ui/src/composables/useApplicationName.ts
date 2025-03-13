import { Core } from "@/writerTypes";
import { computed, onMounted, onUnmounted } from "vue";

function useDebouncer(callback: () => void | Promise<void>, ms: number) {
	let id: ReturnType<typeof setTimeout>;
	return () => {
		if (id) clearTimeout(id);
		id = setTimeout(callback, ms);
	};
}

export function useApplicationName(wf: Core) {
	const abort = new AbortController();

	const root = computed(() => wf.getComponentById("root"));

	async function getApplicationName() {
		// TODO: replace with the real API
		const res = await fetch("https://fakestoreapi.com/users/1", {
			signal: abort.signal,
		});
		if (!res.ok) throw Error("error");
		const data = await res.json();
		return data.username;
	}

	async function updateApplicationName(name: string) {
		// TODO: replace with the real API
		await fetch("https://fakestoreapi.com/users/1", {
			method: "PUT",
			headers: { "Content-Type": "application/json" },
			body: JSON.stringify({ username: name }),
			signal: abort.signal,
		});
	}
	const updateAppName = useDebouncer(async () => {
		await updateApplicationName(name.value);
		await wf.sendComponentUpdate();
	}, 1_000);

	const name = computed<string>({
		get: () => {
			return root.value.content["appName"];
		},
		set: (value) => {
			root.value.content["appName"] = value;
			updateAppName();
		},
	});

	onMounted(async () => {
		name.value = await getApplicationName();
	});

	onUnmounted(() => {
		abort.abort();
	});

	return name;
}
