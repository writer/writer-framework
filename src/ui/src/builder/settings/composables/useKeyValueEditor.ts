import { computed, readonly, ref, shallowRef } from "vue";
import type { JSONValue } from "../BuilderFieldsKeyValue.vue";

type AssistedEntry = { key: string; value: string };
export type Mode = "assisted" | "freehand";

export function useKeyValueEditor(originalValue: JSONValue) {
	const getId = useId();

	const mode = ref<Mode>("assisted");
	function setMode(newMode: Mode) {
		if (mode.value === newMode) return;
		switch (newMode) {
			case "assisted":
				initializeAssistedEntries(currentValue.value);
				break;
			case "freehand":
				freehandValue.value = JSON.stringify(
					currentValue.value,
					undefined,
					2,
				);
				break;
		}
		mode.value = newMode;
	}

	const freehandValue = ref();

	// assisted entries

	const assistedEntries = shallowRef<Record<string, AssistedEntry>>({});
	initializeAssistedEntries(originalValue);

	function addAssistedEntry() {
		assistedEntries.value = {
			...assistedEntries.value,
			[getId()]: { value: "", key: "" },
		};
	}

	function updateAssistedEntryKey(id: string, key: string) {
		const entry = assistedEntries.value[id];
		if (!entry) return;

		assistedEntries.value = {
			...assistedEntries.value,
			[id]: { ...entry, key },
		};
	}
	function updateAssistedEntryValue(id: string, value: string) {
		const entry = assistedEntries.value[id];
		if (!entry) return;

		assistedEntries.value = {
			...assistedEntries.value,
			[id]: { ...entry, value },
		};
	}
	function removeAssistedEntry(id: string) {
		if (!assistedEntries.value[id]) return;
		const copy = { ...assistedEntries.value };
		delete copy[id];
		assistedEntries.value = copy;
	}

	function getAssistedEntryError(id: string): string | undefined {
		const entry = assistedEntries.value[id];
		if (!entry) return;

		if (assitedEntriesDuplicatedKeys.value.has(entry.key)) {
			return "This key is already in use. Please remove duplicate keys.";
		}
	}

	function initializeAssistedEntries(object: JSONValue) {
		assistedEntries.value = Object.entries(object).reduce<
			Record<string, AssistedEntry>
		>((acc, [key, value]) => {
			acc[getId()] = { key, value: String(value) };
			return acc;
		}, {});

		if (Object.keys(assistedEntries.value).length === 0) addAssistedEntry();
	}
	const addAssistedEntryDisabled = computed(() =>
		Object.values(assistedEntries.value).some((k) => k.key === ""),
	);

	const assitedEntriesDuplicatedKeys = computed(() => {
		const keys = new Set<string>();
		const duplicatedKeys = new Set<string>();

		for (const { key } of Object.values(assistedEntries.value)) {
			if (keys.has(key)) {
				duplicatedKeys.add(key);
			} else {
				keys.add(key);
			}
		}

		return duplicatedKeys;
	});

	const isValid = computed(() => {
		switch (mode.value) {
			case "assisted":
				return assitedEntriesDuplicatedKeys.value.size === 0;
			case "freehand":
				try {
					JSON.parse(freehandValue.value);
					return true;
				} catch {
					return false;
				}
			default:
				return false;
		}
	});

	const currentValue = computed<JSONValue>(() => {
		switch (mode.value) {
			case "assisted":
				return Object.values(assistedEntries.value).reduce((acc, v) => {
					acc[v.key] = v.value;
					return acc;
				}, {});
			case "freehand":
				try {
					return JSON.parse(freehandValue.value);
				} catch {
					return {};
				}
			default:
				return {};
		}
	});

	return {
		mode: computed<Mode>({ get: () => mode.value, set: setMode }),
		assistedEntries: readonly(assistedEntries),
		addEntryDisabled: addAssistedEntryDisabled,
		addAssistedEntry,
		updateAssistedEntryKey,
		updateAssistedEntryValue,
		removeAssistedEntry,
		getAssistedEntryError,
		freehandValue,
		isValid,
		currentValue,
	};
}

function useId() {
	let nextId = 0;
	return () => String(++nextId);
}
