/* eslint-disable @typescript-eslint/no-var-requires */
import * as generatorPythonUi from "./generator_python_ui.mjs";
import * as generatorUiComponentJson from "./generator_ui_component_json.mjs";
import * as generatorStorybook from "./generator_storybook.mjs";
import * as generatorUiDocs from "./generator_ui_docs.mjs";

async function generate() {
	await generatorUiDocs.generate();
	await generatorPythonUi.generate();
	await generatorUiComponentJson.generate();
	await generatorStorybook.generate();
}

generate();
