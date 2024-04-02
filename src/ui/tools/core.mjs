/* eslint-disable @typescript-eslint/no-var-requires */
import path from "path";

import { createServer } from "vite";
import { fileURLToPath } from 'url';
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

/**
 * Loads the definition of streamsync components.
 *
 * @returns {Promise<import("./getComponents").Component[]>} The components.
 */
export async function loadComponents() {
	const vite = await createServer({
		includeStreamsyncComponentPath: true,
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
