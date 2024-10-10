module.exports = {
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
		"@typescript-eslint/ban-types": "warn",
		"prettier/prettier": [2, { useTabs: true, endOfLine: "auto" }],
		"no-console": "error",
	},
	parser: "vue-eslint-parser",
	parserOptions: {
		parser: "@typescript-eslint/parser",
		ecmaVersion: 2020,
		sourceType: "module",
	},
	root: true,
	extends: [
		"plugin:@typescript-eslint/recommended",
		"plugin:vue/vue3-recommended",
		"eslint:recommended",
		"@vue/eslint-config-prettier",
		"prettier",
		"plugin:storybook/recommended",
	],
	plugins: ["prettier", "@typescript-eslint", "vue"],
	env: {
		node: true,
	},
};
