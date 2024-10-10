import { registerComponentTemplate } from "./templateMap";

const CUSTOM_COMPONENTS_GLOBAL_VAR = "WriterCustomComponentTemplates";

export async function loadExtensions(extensionPaths: string[]) {
	await Promise.all(
		extensionPaths.map(async (path) => {
			const lcPath = path.toLocaleLowerCase();
			if (lcPath.endsWith(".js")) {
				await importCustomComponentTemplate(path);
			} else if (lcPath.endsWith(".css")) {
				loadStylesheet(path);
			}
		}),
	);
}

async function importCustomComponentTemplate(path: string) {
	console.log(`Importing custom component templates at "${path}"...`);
	await import(/* @vite-ignore */ getRelativeExtensionsPath() + path);
	Object.entries(window[CUSTOM_COMPONENTS_GLOBAL_VAR])?.forEach(
		([key, template]) => {
			if (checkComponentKey(key)) {
				registerComponentTemplate(`custom_${key}`, template);
				console.log(`Registering template for "${key}".`);
			} else {
				console.warn(
					`custom component '${key}' is ignored. A custom component should be declared using only alphanumeric lowercase and _.`,
				);
			}
		},
	);
}

/**
 * 	Checks that the key contains only alphanumeric characters and underscores without capital letters
 * 	The clipboard api use in drag and drop doesn't handle uppercase.
 *
 * 	mycomponent : valid
 * 	myComponent : invalid
 * 	myCOMPONENT : invalid
 *
 * 	@see https://github.com/writer/writer-framework/issues/517
 */
export function checkComponentKey(key: string): boolean {
	const isValidKey = /^[a-z0-9_]+$/.test(key);
	return isValidKey;
}

function loadStylesheet(path: string) {
	const el: HTMLLinkElement = document.createElement("link");
	el.rel = "stylesheet";
	el.href = getRelativeExtensionsPath() + path;
	document.head.appendChild(el);
}

function getRelativeExtensionsPath() {
	let pathname = window.location.pathname;
	if (!pathname.endsWith("/")) {
		pathname += "/";
	}

	return `${pathname}extensions/`;
}


