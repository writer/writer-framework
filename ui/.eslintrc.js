module.exports = {
	rules: {
		indent: ["error", "tab"],
		"prettier/prettier": [2, { useTabs: true }],
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
		"plugin:vue/vue3-essential",
		"prettier/@typescript-eslint",
		"eslint:recommended",
		"@vue/eslint-config-prettier",
		"prettier/vue",
	],
	plugins: ["prettier", "@typescript-eslint"],
	env: {
		node: true,
	},
};
