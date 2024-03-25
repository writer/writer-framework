/* eslint-disable @typescript-eslint/no-var-requires */
const generatorPythonUi = require("./generator_python_ui");
const generatorUiComponentJson = require("./generator_ui_component_json");

async function generate() {
	await generatorPythonUi.generate();
	await generatorUiComponentJson.generate();
}

if (require.main === module) {
	generate();
}
