/**
 * Generates one documentation page per component from sources in docs
 * components
 */

/* eslint-disable @typescript-eslint/no-var-requires */
import components from "writer-ui/components.codegen.json" with { type: "json" };
import * as fs from "fs";
import * as path from "path";
import { fileURLToPath } from "url";
import nunjucks from "nunjucks";
import * as core from "./core.js";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// const frameworkDirectory = path.resolve(__dirname, "..", "framework");
const componentsDirectory = path.resolve(__dirname, "..", "components");


export async function generate() {
	// eslint-disable-next-line no-console
	console.log("generate doc components pages into", componentsDirectory);
	nunjucks.configure({ autoescape: true });

	if (!fs.existsSync(componentsDirectory)) {
		fs.mkdirSync(componentsDirectory);
	}

	components.forEach((component) => {
		if ('toolkit' in component && component.toolkit !== 'core') {
			return
		}

		// eslint-disable-next-line prettier/prettier
		const componentPageTemplate = path.resolve(componentsDirectory, "component_page.mdx.tpl");
		const page = fs.readFileSync(componentPageTemplate, "utf8");

		component.low_code_usage = core.generateLowCodeUsage(component)
		component.event_handler = core.generateEventHandler()

		const renderedPage = nunjucks.renderString(page, component);

		const componentPath = path.resolve(componentsDirectory, `${component.type}.mdx`);
		fs.writeFileSync(componentPath, renderedPage);
	});
}

generate();
