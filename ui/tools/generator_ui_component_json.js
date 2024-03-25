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

	components.forEach((component) => {
		// eslint-disable-next-line prettier/prettier
		const componentFile = 'Core' + component.type[0].toUpperCase() + component.type.slice(1) + '.vue';
		component.source_link = `ui/src/core_components/${component.category.toLowerCase()}/${componentFile}`;
	});

	// eslint-disable-next-line no-console
	console.log("Writing components JSON to", componentsJsonPath);
	await fs.writeFile(componentsJsonPath, JSON.stringify(components, null, 2));
}

if (require.main === module) {
	generate();
}

module.exports = { generate };
