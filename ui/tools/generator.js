/* eslint-disable @typescript-eslint/no-var-requires */
const generatorPythonUi = require("./generator_python_ui");
const generatorUiComponentJson = require("./generator_ui_component_json");
const generatorDocComponentPage = require("./generator_doc_components_page");

async function generate() {
	await generatorPythonUi.generate();
	await generatorUiComponentJson.generate();
	await generatorDocComponentPage.generate();
}

if (require.main === module) {
	generate();
}
