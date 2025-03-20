import { Core } from "@/writerTypes";
import { computed, onMounted, onUnmounted } from "vue";
import { useDebouncer } from "./useDebouncer";

export function useApplicationCloud(wf: Core) {
	const abort = new AbortController();

	const isCloudApp = computed(() =>
		wf.featureFlags.value.includes("writerCloud"),
	);

	const root = computed(() => wf.getComponentById("root"));

	const updateAppName = useDebouncer(async () => {
		if (isCloudApp.value) {
			await updateApplicationName(name.value, { signal: abort.signal });
		}
		await wf.sendComponentUpdate();
	}, 1_000);

	const name = computed<string>({
		get: () => {
			return root.value.content["appName"];
		},
		set: (value) => {
			if (root.value.content["appName"] === value) return;
			root.value.content["appName"] = value;
			updateAppName();
		},
	});

	onMounted(async () => {
		if (!isCloudApp.value) return;

		const distName = await getApplicationName({ signal: abort.signal });
		if (root.value.content["appName"] === distName) return;

		root.value.content["appName"] = distName;
		await wf.sendComponentUpdate();
	});

	onUnmounted(() => {
		abort.abort();
	});

	return { isCloudApp, name };
}

async function getApplicationName(opts: { signal?: AbortSignal } = {}) {
	// TODO: replace with the real API
	const res = await fetch("https://fakestoreapi.com/users/1", {
		signal: opts.signal,
	});
	if (!res.ok) throw Error("error");
	const data = await res.json();
	return data.username;
}

async function updateApplicationName(
	name: string,
	opts: { signal?: AbortSignal } = {},
) {
	// TODO: replace with the real API
	await fetch("https://fakestoreapi.com/users/1", {
		method: "PUT",
		headers: { "Content-Type": "application/json" },
		body: JSON.stringify({ username: name }),
		signal: opts.signal,
	});
}
