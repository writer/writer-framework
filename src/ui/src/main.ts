import * as vue from "vue";
import { createApp } from "vue";
import VueDOMPurifyHTML from "vue-dompurify-html";
import { generateBuilderManager } from "./builder/builderManager.js";
import { generateCore } from "./core";
import "./fonts";
import injectionKeys from "./injectionKeys";
import { setCaptureTabsDirective } from "./directives.js";
import { useLogger } from "./composables/useLogger.js";
import { useApplicationCloud } from "@/composables/useApplicationCloud";
import { useWriterApi } from "@/composables/useWriterApi.js";
import { useCollaboration } from "@/composables/useCollaboration.js";

const wf = generateCore();

// eslint-disable-next-line no-undef
globalThis.vue = vue;
// eslint-disable-next-line no-undef
globalThis.injectionKeys = injectionKeys;
// eslint-disable-next-line no-undef
globalThis.core = wf;

const logger = useLogger();

async function load() {
	await wf.init();

	const mode = wf.mode.value;
	const wfbm = mode == "edit" ? generateBuilderManager() : undefined;

	if (wfbm) {
		wf.addMailSubscription("logEntry", wfbm.handleLogEntry);
		// eslint-disable-next-line no-undef
		globalThis.wfbm = wfbm;
	}

	logger.log(`Mounting app in mode ${mode}...`);

	const { default: componentRenderer } =
		mode === "run" && (await import("./renderer/ComponentRenderer.vue"));
	const { default: builderApp } =
		mode === "edit" && (await import("./builder/BuilderApp.vue"));

	const app = createApp(componentRenderer || builderApp);
	app.use(VueDOMPurifyHTML);
	app.provide(injectionKeys.core, wf);
	app.provide(injectionKeys.builderManager, wfbm);
	setCaptureTabsDirective(app);

	app.mount("#app");

	const { isCloudApp } = useApplicationCloud(wf);
	if (isCloudApp) {
		await enableCollaboration();
	}
}

async function enableCollaboration() {
	const collaboration = useCollaboration(wf);
	const { writerApi } = useWriterApi();
	const writerProfile = await writerApi.profile();
	collaboration.updateOutgoingPing({
		userId: writerProfile.id,
		action: "join",
	});
	collaboration.sendCollaborationPing();
	collaboration.groomSnapshot();
	window.addEventListener("beforeunload", function () {
		collaboration.updateOutgoingPing({ action: "leave" });
		collaboration.sendCollaborationPing();
	});
}

logger.log("Initialising core...");
load()
	.then(async () => {
		logger.log("Core initialised.");
	})
	.catch((reason) => {
		logger.error("Core initialisation failed.", reason);
		document.write(reason);
	});