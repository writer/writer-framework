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

const docDirectory = path.resolve(__dirname, "..", "docs");
const docComponentsDirectory = path.resolve(docDirectory, "components");


export async function generate() {
	// eslint-disable-next-line no-console
	console.log("generate doc components pages into", docComponentsDirectory);
	nunjucks.configure({ autoescape: true });

	if (!fs.existsSync(docComponentsDirectory)) {
		fs.mkdirSync(docComponentsDirectory);
	}

	components.map((component) => {
		// eslint-disable-next-line prettier/prettier
		const componentPageTemplate = path.resolve(docComponentsDirectory, "component_page.mdx.tpl");
		const page = fs.readFileSync(componentPageTemplate, "utf8");

		component.low_code_usage = core.generateLowCodeUsage(component)
		component.event_handler = core.generateEventHandler()

		const renderedPage = nunjucks.renderString(page, component);

		const componentPath = path.resolve(docComponentsDirectory, `${component.type}.mdx`);
		fs.writeFileSync(componentPath, renderedPage);
	});
}

generate();