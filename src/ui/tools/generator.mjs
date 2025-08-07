/* eslint-disable @typescript-eslint/no-var-requires */
import * as generatorPythonUi from "./generator_python_ui.mjs";
import * as generatorUiComponentJson from "./generator_ui_component_json.mjs";

async function generate() {
	await generatorPythonUi.generate();
	await generatorUiComponentJson.generate();
}

generate();
