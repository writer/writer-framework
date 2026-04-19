import js from "@eslint/js";
import tseslint from "@typescript-eslint/eslint-plugin";
import tsparser from "@typescript-eslint/parser";
import vueParser from "vue-eslint-parser";
import vuePlugin from "eslint-plugin-vue";
import prettierPlugin from "eslint-plugin-prettier";
import prettierConfig from "@vue/eslint-config-prettier";
import globals from "globals";

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
				...globals.browser,
				...globals.node,
				// Additional browser APIs that may not be in globals.browser
				MediaStreamConstraints: "readonly",
				RequestInit: "readonly",
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
