import * as vue from "vue";
import { createApp } from "vue";
import VueDOMPurifyHTML from "vue-dompurify-html";
import { generateBuilderManager } from "./builder/builderManager.js";
import { generateCore } from "./core";
import "./fonts";
import injectionKeys from "./injectionKeys";
import { useLogger } from "./composables/useLogger.js";
import { useWriterApi } from "./composables/useWriterApi.js";
import { useCollaborationManager } from "./composables/useCollaborationManager.js";
import { useNotesManager } from "./core/useNotesManager.js";
import { CollaborationManager } from "./writerTypes.js";
import { useSecretsManager } from "./core/useSecretsManager.js";
import { RECONNECT_DELAY_MS, MAX_RETRIES } from "@/constants/retry";

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
	const secretsManager = mode == "edit" ? useSecretsManager(wf) : undefined;
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

	app.mount("#app");

	if (wf.isWriterCloudApp.value && collaborationManager) {
		await enableCollaboration(collaborationManager).catch(logger.error);
	}
	if (wf.isWriterCloudApp.value && secretsManager) {
		secretsManager.load().catch(logger.error);
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

async function initialise() {
	for (let attempt = 0; attempt < MAX_RETRIES; attempt++) {
		try {
			await load();
			return;
		} catch (reason) {
			if (attempt < MAX_RETRIES - 1) {
				logger.warn(
					`Core initialization failed (attempt ${attempt + 1}/${MAX_RETRIES}). Retrying...`,
					reason,
				);
				const loaderEl = document.getElementById("loading_L1");
				if (loaderEl && !document.getElementById("loading_message") && attempt >= 2) {
					const message = document.createElement("div");
					message.id = "loading_message";
					message.textContent =
						"We're getting things ready.\nHang tight while we connect...";
					message.style.cssText =
						"position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);margin-top:120px;text-align:center;font-family: 'Poppins','Helvetica Neue','Lucida Grande',sans-serif;color:#666;font-size:14px;line-height:1.4;max-width:400px;padding:0 20px;z-index:1000;white-space:pre-line;opacity:0;transition:opacity 0.5s ease-in;";
					document.body.appendChild(message);
					// Trigger fade-in animation
					setTimeout(() => {
						message.style.opacity = "1";
					}, 50);
				}
				await new Promise((r) =>
					setTimeout(r, RECONNECT_DELAY_MS * (attempt + 1)),
				);
				continue;
			}
			throw reason;
		}
	}
}

logger.log("Initialising core...");
initialise()
	.then(async () => {
		logger.log("Core initialised.");
	})
	.catch((reason) => {
		logger.error("Core initialisation failed.", reason);
		
		const errorDiv = document.createElement("div");
		errorDiv.className = "error-message";
		errorDiv.setAttribute("role", "alert");
		errorDiv.style.cssText =
			'padding: 20px; color: #d32f2f; background: #ffebee; border: 1px solid #e57373; border-radius: 4px; margin: 20px; font-family: "Poppins", "Helvetica Neue", "Lucida Grande", sans-serif;';

		const message = document.createElement("div");
		message.textContent =
			"Failed to initialise application" +
			(reason?.message ? `: ${reason.message}` : "");

		const instructions = document.createElement("div");
		instructions.style.marginTop = "12px";
		instructions.textContent =
			"This might mean the Agent Builder is still being prepared. Try reloading the page in a few seconds.";

		const reloadButton = document.createElement("button");
		reloadButton.textContent = "Reload page";
		reloadButton.className =
			"WdsButton WdsButton--small WdsButton--tertiary";
		reloadButton.style.cssText =
			"margin-top: 16px; font-size: .875rem; font-weight: 600; border-radius: 300px; padding: 4px 16px; height: 32px; background: var(--wdsColorWhite); color: var(--wdsColorBlack); border-color: var(--wdsColorGray2); border-width: 1px; border-style: solid; box-shadow: var(--buttonShadow); cursor: pointer; display: flex; align-items: center; justify-content: center; gap: 8px; outline: none; position: relative; overflow: hidden; max-width: 100%; width: fit-content;";
		reloadButton.onclick = () => window.location.reload();

		errorDiv.appendChild(message);
		errorDiv.appendChild(instructions);
		errorDiv.appendChild(reloadButton);

		const loadingSpinner = document.getElementById("loading_L1");
		loadingSpinner?.remove();
		// Remove loading message if it exists
		const loadingMessage = document.getElementById("loading_message");
		if (loadingMessage) {
			loadingMessage.remove();
		}
		document.body.appendChild(errorDiv);
	});
