import { importVue } from "./core.mjs";

async function checkDeclarationKey() {
	let hasFailed = false;
	const module = await importVue("../src/components/custom/index.ts");
	const { checkComponentKey } = await importVue(
		"../src/core/loadExtensions.ts",
	);
	const invalidCustomComponentKeys = [];
	Object.keys(module.default).forEach((key) => {
		if (!checkComponentKey(key)) {
			invalidCustomComponentKeys.push(key);
			hasFailed = true;
		}
	});

	if (invalidCustomComponentKeys.length !== 0) {
		// eslint-disable-next-line no-console
		console.error(
			`ERROR: Invalid component declaration: ${invalidCustomComponentKeys} into 'src/components/custom/index.ts'. Their key must be declared using only lowercase and alphanumeric characters.`,
		);
	}
	return hasFailed;
}

/**
 * Check the custom components in continuous integration
 *
 * npm run custom.check
 *
 */
async function check() {
	let hasFailed = false;

	hasFailed |= await checkDeclarationKey();

	if (hasFailed) {
		process.exit(1);
	}
}

check();
