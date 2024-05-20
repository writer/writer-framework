/* eslint-disable @typescript-eslint/no-var-requires */
import { promises as fs } from "fs";
import path from "path";
import { fileURLToPath } from "url";

import { loadComponents } from "./core.mjs";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// eslint-disable-next-line prettier/prettier
const componentsJsonPath = path.resolve(__dirname, "..", "components.codegen.json");

/**
 * Exports an inventory of Writer Framework components into json.
 *
 * @returns {Promise<void>}
 */
export async function generate() {
	const components = await loadComponents();

	// eslint-disable-next-line no-console
	console.log("Writing components JSON to", componentsJsonPath);
	await fs.writeFile(componentsJsonPath, JSON.stringify(components, null, 2));
}
