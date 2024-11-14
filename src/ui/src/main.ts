import * as vue from "vue";
import { createApp } from "vue";
import VueDOMPurifyHTML from "vue-dompurify-html";
import { generateBuilderManager } from "./builder/builderManager.js";
import { generateCore } from "./core";
import "./fonts";
import injectionKeys from "./injectionKeys";
import { setCaptureTabsDirective } from "./directives.js";

/**
 * RemixIcon by remixicon.com
 */
import "remixicon/fonts/remixicon.css";

const wf = generateCore();

globalThis.vue = vue;
globalThis.injectionKeys = injectionKeys;
globalThis.core = wf;

async function load() {
	await wf.init();
	const mode = wf.mode.value;
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
