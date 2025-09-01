import { computed, readonly, ref, shallowRef } from "vue";
import type { JSONValue } from "../BuilderFieldsKeyValue.vue";
import { TEMPLATE_REGEX } from "@/renderer/useEvaluator";

type AssistedEntry = { key: string; value: string };
export type Mode = "assisted" | "freehand";

function isValidJSON(value: string) {
	try {
		JSON.parse(value);
		return true;
	} catch {
		return false;
	}
}
function tryToParse(value: string) {
	try {
		return JSON.parse(value);
	} catch {
		return {};
	}
}

function isFlatRecordString(obj: object): obj is Record<string, string> {
	return Object.values(obj).every((v) => typeof v === "string");
}

export function useKeyValueEditor(originalValue: string | JSONValue) {
	const getId = useId();

	const mode = ref<Mode>(computeInitialMode(originalValue));
	const freehandValue = ref(
		typeof originalValue === "string"
			? originalValue
			: JSON.stringify(originalValue),
	);
	const assistedEntries = shallowRef<Record<string, AssistedEntry>>({});

	initializeAssistedEntries(originalValue);

	function setMode(newMode: Mode) {
		if (mode.value === newMode) return;
		switch (newMode) {
			case "assisted":
				initializeAssistedEntries(currentValue.value);
				break;
			case "freehand":
				freehandValue.value = JSON.stringify(
					currentValueObject.value,
					undefined,
					2,
				);
				break;
		}
		mode.value = newMode;
	}

	// assisted entries

	function updateAssistedEntries(value: Record<string, unknown>) {
		assistedEntries.value = Object.entries(value).reduce(
			(acc, [key, value]) => {
				acc[getId()] = { key, value: String(value) };
				return acc;
			},
			{},
		);
	}

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

	function computeInitialMode(objectOrString: string | JSONValue): Mode {
		if (typeof objectOrString !== "string") {
			return isFlatRecordString(objectOrString) ? "assisted" : "freehand";
		}

		if (TEMPLATE_REGEX.exec(objectOrString)) return "freehand";
		if (!isValidJSON(objectOrString)) return "freehand";

		return isFlatRecordString(tryToParse(objectOrString))
			? "assisted"
			: "freehand";
	}

	function initializeAssistedEntries(objectOrString: string | JSONValue) {
		const object =
			typeof objectOrString === "string"
				? tryToParse(objectOrString)
				: objectOrString;

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
				return true;
			default:
				return false;
		}
	});

	const currentValue = computed<string>(() => {
		switch (mode.value) {
			case "assisted": {
				const obj = Object.values(assistedEntries.value)
					.filter((v) => !(v.key === "" && v.value === ""))
					.reduce((acc, v) => {
						acc[v.key] = v.value;
						return acc;
					}, {});
				return JSON.stringify(obj);
			}
			case "freehand":
				return freehandValue.value;

			default:
				return "";
		}
	});

	const currentValueObject = computed<JSONValue>(() =>
		tryToParse(currentValue.value),
	);

	return {
		mode: computed<Mode>({ get: () => mode.value, set: setMode }),
		assistedEntries: readonly(assistedEntries),
		addEntryDisabled: addAssistedEntryDisabled,
		addAssistedEntry,
		updateAssistedEntryKey,
		updateAssistedEntryValue,
		removeAssistedEntry,
		getAssistedEntryError,
		updateAssistedEntries,
		freehandValue,
		isValid,
		currentValue,
		currentValueObject,
	};
}

function useId() {
	let nextId = 0;
	return () => String(++nextId);
}
