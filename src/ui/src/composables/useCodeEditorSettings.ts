/**
 * Composable for managing code editor settings (diagnostics, AI completion)
 * Settings are persisted to localStorage and apply immediately.
 *
 * Usage:
 * 1. Call setupCodeEditorSettings() once in your root component (e.g., BuilderApp.vue)
 * 2. Use useCodeEditorSettings() in any child component to access/modify settings
 */
import {
	computed,
	inject,
	provide,
	ref,
	watch,
	type InjectionKey,
	type Ref,
} from "vue";
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

// Injection keys for provide/inject
const diagnosticsEnabledKey = Symbol("diagnosticsEnabled") as InjectionKey<
	Ref<boolean>
>;
const aiCompletionEnabledKey = Symbol("aiCompletionEnabled") as InjectionKey<
	Ref<boolean>
>;

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

/**
 * Sets up the code editor settings system.
 * Must be called once in the root component (e.g., BuilderApp.vue).
 * Creates reactive refs and watchers for syncing with localStorage.
 */
export function setupCodeEditorSettings() {
	// Load from localStorage
	const settings = useLocalStorageJSON<CodeEditorSettings>(
		STORAGE_KEY,
		validateSettings,
	);

	// Initialize with defaults if not set
	if (!settings.value) {
		settings.value = { ...DEFAULT_SETTINGS };
	}

	// Create reactive refs
	const diagnosticsEnabledRef = ref(
		settings.value?.diagnosticsEnabled ??
			DEFAULT_SETTINGS.diagnosticsEnabled,
	);
	const aiCompletionEnabledRef = ref(
		settings.value?.aiCompletionEnabled ??
			DEFAULT_SETTINGS.aiCompletionEnabled,
	);

	// Sync changes to localStorage (watchers are scoped to this setup call)
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

	// Provide the refs for child components to inject
	provide(diagnosticsEnabledKey, diagnosticsEnabledRef);
	provide(aiCompletionEnabledKey, aiCompletionEnabledRef);
}

/**
 * Hook to access and modify code editor settings.
 * Settings are stored in localStorage and reactive across all instances.
 *
 * Must be used in a component that is a descendant of the component
 * where setupCodeEditorSettings() was called.
 */
export function useCodeEditorSettings() {
	const diagnosticsEnabledRef = inject(diagnosticsEnabledKey);
	const aiCompletionEnabledRef = inject(aiCompletionEnabledKey);

	if (!diagnosticsEnabledRef || !aiCompletionEnabledRef) {
		throw new Error(
			"useCodeEditorSettings() must be called in a component where setupCodeEditorSettings() has been set up in a parent component",
		);
	}

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
