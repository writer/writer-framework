import js from "@eslint/js";
import tseslint from "@typescript-eslint/eslint-plugin";
import tsparser from "@typescript-eslint/parser";
import vueParser from "vue-eslint-parser";
import vuePlugin from "eslint-plugin-vue";
import prettierPlugin from "eslint-plugin-prettier";
import prettierConfig from "@vue/eslint-config-prettier";

export default [
	js.configs.recommended,

	...vuePlugin.configs["flat/recommended"],

	{
		ignores: [
			"**/node_modules/**",
			"**/dist/**",
			"**/build/**",
			"**/.vite/**",
			"**/custom_components_dist/**",
		],
	},

	{
		files: [
			"**/*.vue",
			"**/*.ts",
			"**/*.js",
			"**/*.jsx",
			"**/*.cjs",
			"**/*.mjs",
		],

		languageOptions: {
			parser: vueParser,
			parserOptions: {
				parser: tsparser,
				ecmaVersion: 2020,
				sourceType: "module",
			},
			globals: {
				process: "readonly",
				__dirname: "readonly",
				__filename: "readonly",
				module: "readonly",
				require: "readonly",
				window: "readonly",
				document: "readonly",
				navigator: "readonly",
				console: "readonly",
				localStorage: "readonly",
				sessionStorage: "readonly",
				fetch: "readonly",
				Response: "readonly",
				Request: "readonly",
				FormData: "readonly",
				location: "readonly",
				setTimeout: "readonly",
				clearTimeout: "readonly",
				setInterval: "readonly",
				clearInterval: "readonly",
				requestAnimationFrame: "readonly",
				cancelAnimationFrame: "readonly",
				getComputedStyle: "readonly",
				self: "readonly",
				HTMLElement: "readonly",
				Element: "readonly",
				Node: "readonly",
				MouseEvent: "readonly",
				KeyboardEvent: "readonly",
				DragEvent: "readonly",
				PointerEvent: "readonly",
				Event: "readonly",
				AbortController: "readonly",
				ResizeObserver: "readonly",
				MutationObserver: "readonly",
				IntersectionObserver: "readonly",
				URL: "readonly",
				URLSearchParams: "readonly",
				Blob: "readonly",
				File: "readonly",
				FileReader: "readonly",
				TextDecoder: "readonly",
				TextEncoder: "readonly",
				Image: "readonly",
				atob: "readonly",
				btoa: "readonly",
				InputEvent: "readonly",
				CustomEvent: "readonly",
				HTMLInputElement: "readonly",
				HTMLLinkElement: "readonly",
				AbortSignal: "readonly",
				RequestInit: "readonly",
				structuredClone: "readonly",
				BeforeUnloadEvent: "readonly",
				WebSocket: "readonly",
				CloseEvent: "readonly",
				ErrorEvent: "readonly",
				PromiseRejectionEvent: "readonly",
				performance: "readonly",
				FileList: "readonly",
				alert: "readonly",
				confirm: "readonly",
				prompt: "readonly",
				HTMLDivElement: "readonly",
				HTMLButtonElement: "readonly",
				HTMLTextAreaElement: "readonly",
				HTMLImageElement: "readonly",
				WheelEvent: "readonly",
				FocusEvent: "readonly",
				DOMRect: "readonly",
				ClipboardEvent: "readonly",
				MediaDeviceInfo: "readonly",
				MediaStreamConstraints: "readonly",
				MediaStream: "readonly",
				Storage: "readonly",
				global: "readonly",
			},
		},

		plugins: {
			"@typescript-eslint": tseslint,
			vue: vuePlugin,
			prettier: prettierPlugin,
		},

		rules: {
			indent: "off",
			"no-unused-vars": "off",

			"@typescript-eslint/no-unused-vars": [
				"warn",
				{
					args: "all",
					argsIgnorePattern: "^_",
					caughtErrors: "all",
					caughtErrorsIgnorePattern: "^_",
					destructuredArrayIgnorePattern: "^_",
					varsIgnorePattern: "^_",
					ignoreRestSiblings: true,
				},
			],
			"@typescript-eslint/no-explicit-any": "warn",

			"prettier/prettier": [
				2,
				{
					useTabs: true,
					endOfLine: "auto",
				},
			],

			"no-console": "error",
		},
	},

	prettierConfig,
];
