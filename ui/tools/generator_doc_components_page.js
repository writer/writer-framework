/* eslint-disable @typescript-eslint/no-var-requires */
const { loadComponents } = require("./core");
const path = require("path");
const fs = require("fs");

const componentPageTemplate = path.resolve(__dirname, "component_page.tpl.md");
const docDirectory = path.resolve(__dirname, "..", "..", "docs", "docs");
const docComponentsDirectory = path.resolve(docDirectory, "components");

async function generate() {
	const components = await loadComponents();
	// eslint-disable-next-line no-console
	console.log("generate doc components pages into", docComponentsDirectory);

	if (!fs.existsSync(docComponentsDirectory)) {
		fs.mkdirSync(docComponentsDirectory);
	}

	components.map((component) => {
		// eslint-disable-next-line prettier/prettier
		const componentPath = path.resolve(docComponentsDirectory, `${component.type}.md`);
		const page = fs.readFileSync(componentPageTemplate, "utf8");
		let renderTemplate = new Function(
			"component",
			"return `" + page + "`;",
		);

		fs.writeFileSync(componentPath, renderTemplate(component));
	});
}

if (require.main === module) {
	generate();
}

module.exports = { generate };
