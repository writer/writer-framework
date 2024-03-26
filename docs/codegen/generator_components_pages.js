/**
 * Generates one documentation page per component from sources in docs
 * components
 */

/* eslint-disable @typescript-eslint/no-var-requires */
const components = require("streamsync-ui/components.codegen.json");
const path = require("path");
const fs = require("fs");

const docDirectory = path.resolve(__dirname, "..", "docs");
const docComponentsDirectory = path.resolve(docDirectory, "components");
const componentPageTemplate = path.resolve(
	docComponentsDirectory,
	"component_page.md.tpl",
);

async function generate() {
	// eslint-disable-next-line no-console
	console.log("generate doc components pages into", docComponentsDirectory);

	if (!fs.existsSync(docComponentsDirectory)) {
		fs.mkdirSync(docComponentsDirectory);
	}

	components.map((component) => {
		// eslint-disable-next-line prettier/prettier
		const componentPath = path.resolve(docComponentsDirectory, `${component.type}.md`);
		const page = fs.readFileSync(componentPageTemplate, "utf8");
		const renderedPage = page.replace("@{component_name}", component.name);

		fs.writeFileSync(componentPath, renderedPage);
	});
}

if (require.main === module) {
	generate();
}

module.exports = { generate };
