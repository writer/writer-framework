/* eslint-disable @typescript-eslint/no-var-requires */
const path = require("path");
const fs = require("fs").promises;

const { loadComponents } = require("./core");

// eslint-disable-next-line prettier/prettier
const componentsJsonPath = path.resolve(__dirname, "..", "components.codegen.json");

/**
 * Exports an inventory of Streamsync components into json.
 *
 * @returns {Promise<void>}
 */
async function generate() {
	const components = await loadComponents();

	// eslint-disable-next-line no-console
	console.log("Writing components JSON to", componentsJsonPath);
	await fs.writeFile(componentsJsonPath, JSON.stringify(components, null, 2));
}

if (require.main === module) {
	generate();
}

module.exports = { generate };
