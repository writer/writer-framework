import * as vue from "vue";
import { App, createApp } from "vue";
import injectionKeys from "./injectionKeys";
import { generateCore } from "./core";
import { generateBuilderManager } from "./builder/builderManager.js";
import VueDOMPurifyHTML from "vue-dompurify-html";

/**
 * RemixIcon by remixicon.com
 */
import "remixicon/fonts/remixicon.css";

function setCaptureTabsDirective(app: App<Element>) {
	app.directive("capture-tabs", {
		mounted: (el: HTMLTextAreaElement) => {
			el.addEventListener("keydown", (ev) => {
				if (ev.key != "Tab") return;
				ev.preventDefault();
				el.setRangeText(
					"  ",
					el.selectionStart,
					el.selectionStart,
					"end",
				);
			});
		},
	});
}

const wf = generateCore();

globalThis.vue = vue;
globalThis.injectionKeys = injectionKeys;
globalThis.core = wf;

async function load() {
	await wf.init();
	const mode = wf.getMode();
	const ssbm = mode == "edit" ? generateBuilderManager() : undefined;

	if (ssbm) {
		wf.addMailSubscription("logEntry", ssbm.handleLogEntry);
	}

	console.log(`Mounting app in mode ${mode}...`);

	const { default: componentRenderer } =
		mode === "run" && (await import("./renderer/ComponentRenderer.vue"));
	const { default: builderApp } =
		mode === "edit" && (await import("./builder/BuilderApp.vue"));

	const app = createApp(componentRenderer || builderApp);
	app.use(VueDOMPurifyHTML);
	app.provide(injectionKeys.core, wf);
	app.provide(injectionKeys.builderManager, ssbm);
	setCaptureTabsDirective(app);

	app.mount("#app");
}

console.log("Initialising Writer Framework core...");
load()
	.then(async () => {
		console.log("Core initialised.");
	})
	.catch((reason) => {
		console.error("Core initialisation failed.", reason);
		document.write(reason);
	});
