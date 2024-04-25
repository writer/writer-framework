/**
 * Generates one documentation page per component from sources in docs
 * components
 */

/* eslint-disable @typescript-eslint/no-var-requires */
import components from "streamsync-ui/components.codegen.json" with { type: "json" };
import * as fs from "fs";
import * as path from "path";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const docDirectory = path.resolve(__dirname, "..", "docs");
const docComponentsDirectory = path.resolve(docDirectory, "components");
const componentPageTemplate = path.resolve(
	docComponentsDirectory,
	"component_page.md.tpl",
);

export async function generate() {
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

generate();
