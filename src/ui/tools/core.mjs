/* eslint-disable @typescript-eslint/no-var-requires */
import path from "path";

import { createServer } from "vite";
import { fileURLToPath } from "url";
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

/**
 * Loads the definition of Writer Framework components.
 *
 * @returns {Promise<import("./getComponents").Component[]>} The components.
 */
export async function loadComponents() {
	const vite = await createServer({
		includeWriterComponentPath: true,
		server: {
			middlewareMode: true,
		},
		appType: "custom",
	});

	const { data } = await vite.ssrLoadModule(
		path.join(__dirname, "getComponents.ts"),
	);

	await vite.close();

	return data;
}

/**
 * imports a vue-dependent module.
 */
export async function importVue(modulePath) {
	const vite = await createServer({
		includeWriterComponentPath: true,
		server: {
			middlewareMode: true,
		},
		appType: "custom",
	});

	const m = await vite.ssrLoadModule(path.join(__dirname, modulePath));
	await vite.close();

	return m;
}
