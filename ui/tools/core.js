/* eslint-disable @typescript-eslint/no-var-requires */
const path = require("path");

const { createServer } = require("vite");

/**
 * Loads the definition of streamsync components.
 */
async function loadComponents() {
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

module.exports = { loadComponents };
