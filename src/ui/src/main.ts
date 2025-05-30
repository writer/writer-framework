import * as vue from "vue";
import { createApp } from "vue";
import VueDOMPurifyHTML from "vue-dompurify-html";
import { generateBuilderManager } from "./builder/builderManager.js";
import { generateCore } from "./core";
import "./fonts";
import injectionKeys from "./injectionKeys";
import { setCaptureTabsDirective } from "./directives.js";
import { useLogger } from "./composables/useLogger.js";
import { useWriterApi } from "./composables/useWriterApi.js";
import { useCollaborationManager } from "./composables/useCollaborationManager.js";
import { useNotesManager } from "./core/useNotesManager.js";
import { CollaborationManager } from "./writerTypes.js";
import { useSecretsManager } from "./core/useSecretsManager.js";

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
	const notesManager = useNotesManager(wf, wfbm);
	const secretsManager = useSecretsManager();
	const collaborationManager =
		mode == "edit" ? useCollaborationManager(wf) : undefined;

	if (wfbm) {
		wf.addMailSubscription("logEntry", wfbm.handleLogEntry);
		wf.addCollaborationPingSubscription(
			collaborationManager.handleIncomingCollaborationUpdate,
		);

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
	app.provide(injectionKeys.notesManager, notesManager);
	app.provide(injectionKeys.collaborationManager, collaborationManager);
	app.provide(injectionKeys.secretsManager, secretsManager);
	setCaptureTabsDirective(app);

	app.mount("#app");

	if (wf.isWriterCloudApp.value && collaborationManager) {
		await enableCollaboration(collaborationManager);
	}
}

async function enableCollaboration(collaborationManager: CollaborationManager) {
	const { writerApi } = useWriterApi();
	const writerProfile = await writerApi.fetchUserProfile();
	collaborationManager.updateOutgoingPing({
		userId: writerProfile.id.toString(),
		action: "join",
	});
	collaborationManager.sendCollaborationPing();
	collaborationManager.groomSnapshot();
	window.addEventListener("beforeunload", function () {
		collaborationManager.updateOutgoingPing({ action: "leave" });
		collaborationManager.sendCollaborationPing();
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
