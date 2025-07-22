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

	if (!Array.isArray(data)) {
		throw new Error(
			`Expected data to be an array, got ${typeof data} instead.`,
		);
	}

	return data.map((component) => {
		return {
			...component,
			displayName: component.name,
			internalName: normalizeComponentName(component.name),
		};
	});
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

/**
 * Converts a component display name into a stable, PascalCase identifier except for acronyms (e.g., JSON, HTTP)
 *
 * @param {string} name
 * @returns {string}
 */
export function normalizeComponentName(name) {
	if (typeof name !== "string") {
		throw new Error(`Component name must be a string, got ${typeof name}`);
	}

	const normalizedName = name
		.split(/\s+/)
		.map((word) => {
			const isAcronym =
				word === word.toUpperCase() &&
				word.length > 1 &&
				/^[A-Z]+$/.test(word);

			if (isAcronym) {
				return word;
			}

			return `${word.charAt(0).toUpperCase()}${word.slice(1)}`;
		})
		.join("");

	const manualOverrides = {
		AnnotatedText: "Annotatedtext",
		TextAreaInput: "TextareaInput",
	};

	return manualOverrides[normalizedName]
		? manualOverrides[normalizedName]
		: normalizedName;
}
