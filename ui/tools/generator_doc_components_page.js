/* eslint-disable @typescript-eslint/no-var-requires */
const { loadComponents } = require("./core");
const path = require("path");

const docDirectory = path.resolve(__dirname, "..", "..", "docs");
const docComponentsDirectory = path.resolve(docDirectory, "components");

async function generate() {
	const components = await loadComponents();
	// eslint-disable-next-line no-console
	// console.log(components);
}

if (require.main === module) {
	generate();
}

module.exports = { generate };
