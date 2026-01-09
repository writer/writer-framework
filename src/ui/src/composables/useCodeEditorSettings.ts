/**
 * Composable for managing code editor settings (diagnostics, AI completion)
 * Settings are persisted to localStorage and apply immediately.
 * All instances share the same reactive state.
 */
import { computed, ref, watch } from "vue";
import { useLocalStorageJSON } from "./useStorageJSON";

export interface CodeEditorSettings {
	diagnosticsEnabled: boolean;
	aiCompletionEnabled: boolean;
}

const DEFAULT_SETTINGS: CodeEditorSettings = {
	diagnosticsEnabled: true,
	aiCompletionEnabled: false,
};

const STORAGE_KEY = "codeEditorSettings";

/**
 * Validates that the stored settings have the correct shape
 */
function validateSettings(value: unknown): value is CodeEditorSettings {
	if (typeof value !== "object" || value === null) return false;
	const obj = value as Record<string, unknown>;
	return (
		typeof obj.diagnosticsEnabled === "boolean" &&
		typeof obj.aiCompletionEnabled === "boolean"
	);
}

// Shared reactive state that persists to localStorage
// This is created once and shared across all component instances
const settings = useLocalStorageJSON<CodeEditorSettings>(
	STORAGE_KEY,
	validateSettings,
);

// Initialize with defaults if not set
if (!settings.value) {
	settings.value = { ...DEFAULT_SETTINGS };
}

// Create shared reactive refs
const diagnosticsEnabledRef = ref(
	settings.value?.diagnosticsEnabled ?? DEFAULT_SETTINGS.diagnosticsEnabled,
);
const aiCompletionEnabledRef = ref(
	settings.value?.aiCompletionEnabled ?? DEFAULT_SETTINGS.aiCompletionEnabled,
);

// Sync changes to localStorage
watch(diagnosticsEnabledRef, (value) => {
	settings.value = {
		...settings.value,
		diagnosticsEnabled: value,
	} as CodeEditorSettings;
});

watch(aiCompletionEnabledRef, (value) => {
	settings.value = {
		...settings.value,
		aiCompletionEnabled: value,
	} as CodeEditorSettings;
});

/**
 * Hook to access and modify code editor settings.
 * Settings are stored in localStorage and reactive across all instances.
 */
export function useCodeEditorSettings() {
	const diagnosticsEnabled = computed({
		get: () => diagnosticsEnabledRef.value,
		set: (value: boolean) => {
			diagnosticsEnabledRef.value = value;
		},
	});

	const aiCompletionEnabled = computed({
		get: () => aiCompletionEnabledRef.value,
		set: (value: boolean) => {
			aiCompletionEnabledRef.value = value;
		},
	});

	return {
		diagnosticsEnabled,
		aiCompletionEnabled,
	};
}
