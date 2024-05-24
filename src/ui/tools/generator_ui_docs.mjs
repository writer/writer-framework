/* eslint-disable @typescript-eslint/no-var-requires */
import { promises as fs } from "fs";
import path from "path";
import { fileURLToPath } from "url";
import { createSSRApp } from "vue";
import { renderToString } from "@vue/server-renderer";
import { loadComponents } from "./core.mjs";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

async function generateComponent(component) {
	const exportPath = path.resolve(__dirname, "docs", `${component.type}.mdx`);

	const app = createSSRApp({
		data: () => component,
		template: `<div>{{ type }}</div>`,
	});

	const html = await renderToString(app);

	await fs.writeFile(exportPath, html);
}

export async function generate() {
	const components = await loadComponents();

	components.forEach(async (component) => {
		await generateComponent(component);
	});
}
