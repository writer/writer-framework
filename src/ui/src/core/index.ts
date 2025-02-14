/* eslint-disable @typescript-eslint/ban-types */
/* eslint-disable @typescript-eslint/no-explicit-any */
import { readonly, ref, Ref, shallowRef, toRaw } from "vue";
import {
	AbstractTemplate,
	Component,
	ComponentMap,
	InstancePath,
	MailItem,
	SourceFiles,
	UserFunction,
} from "@/writerTypes";
import {
	getSupportedComponentTypes,
	getComponentDefinition,
	registerAbstractComponentTemplate,
} from "./templateMap";
import * as typeHierarchy from "./typeHierarchy";
import { auditAndFixComponents } from "./auditAndFix";
import { parseAccessor } from "./parsing";
import { loadExtensions } from "./loadExtensions";
import { bigIntReplacer } from "./serializer";
import { useLogger } from "@/composables/useLogger";
import {
	createFileToSourceFiles,
	deleteFileToSourceFiles,
	findSourceFileFromPath,
	isSourceFilesFile,
	moveFileToSourceFiles,
} from "./sourceFiles";

const RECONNECT_DELAY_MS = 1000;
const KEEP_ALIVE_DELAY_MS = 60000;

export function generateCore() {
	let sessionId: string = null;
	const sessionTimestamp: Ref<number> = ref(null);
	/**
	 * Whether Writer Framework is running as builder or runner.
	 * The mode is enforced in the backend and used in the frontend for presentation purposes only.
	 *
	 * @returns
	 */
	const mode: Ref<"run" | "edit"> = ref(null);
	const featureFlags = shallowRef<string[]>([]);
	const runCode: Ref<string> = ref(null);
	const sourceFiles = shallowRef<SourceFiles>({
		type: "directory",
		children: {},
	});
	const components: Ref<ComponentMap> = ref({});
	const userFunctions: Ref<UserFunction[]> = ref([]);
	const userState: Ref<Record<string, any>> = ref({});
	let webSocket: WebSocket;
	const syncHealth: Ref<"idle" | "connected" | "offline" | "suspended"> =
		ref("idle");
	let frontendMessageCounter = 0;
	const frontendMessageMap: Ref<Map<number, { callback?: Function }>> = ref(
		new Map(),
	);
	let mailInbox: MailItem[] = [];
	const mailSubscriptions: { mailType: string; fn: Function }[] = [];
	const activePageId: Ref<Component["id"]> = ref(null);

	/**
	 * Initialise the core.
	 * @returns
	 */
	async function init() {
		await initSession();
		addMailSubscription("pageChange", (pageKey: string) => {
			setActivePageFromKey(pageKey);
		});
		sendKeepAliveMessage();
		if (mode.value != "edit") return;
	}

	/**
	 * Initialise a session by loading a starter pack from the backend.
	 *
	 * @returns
	 */
	async function initSession() {
		const response = await fetch("./api/init", {
			method: "post",
			cache: "no-store",
			headers: {
				"Content-Type": "application/json",
			},
			body: JSON.stringify({
				proposedSessionId: sessionId,
			}),
		});
		const initData = await response.json();

		if (response.status > 400) {
			throw "Connection rejected.";
		}

		if (initData.extensionPaths) {
			await loadExtensions(initData.extensionPaths);
		}

		mode.value = initData.mode;
		components.value = initData.components;
		userState.value = initData.userState;
		collateMail(initData.mail);
		sessionId = initData.sessionId;
		sessionTimestamp.value = new Date().getTime();
		featureFlags.value = initData.featureFlags;
		loadAbstractTemplates(initData.abstractTemplates);

		// Only returned for edit (Builder) mode

		userFunctions.value = initData.userFunctions;
		runCode.value = initData.runCode;
		sourceFiles.value = initData.sourceFiles;

		await startSync();

		if (mode.value != "edit") return;
		const isFixApplied = auditAndFixComponents(initData.components);
		if (!isFixApplied) return;
		await sendComponentUpdate();
	}

	function loadAbstractTemplates(
		abstractTemplates: Record<string, AbstractTemplate>,
	) {
		Object.entries(abstractTemplates ?? {}).forEach(
			([type, abstractTemplate]) => {
				registerAbstractComponentTemplate(type, abstractTemplate);
			},
		);
	}

	function sendKeepAliveMessage() {
		setTimeout(() => {
			sendFrontendMessage("keepAlive", {}, sendKeepAliveMessage);
		}, KEEP_ALIVE_DELAY_MS);
	}

	function ingestMutations(mutations: Record<string, any>) {
		if (!mutations) return;
		Object.entries(mutations).forEach(([key, value]) => {
			/*
			Splits the key while respecting escaped dots.
			For example, "files.myfile\.sh" will be split into ["files", "myfile.sh"] 
			*/

			const mutationFlag = key.charAt(0);
			const accessor = parseAccessor(key.substring(1));
			const lastElementIndex = accessor.length - 1;
			let stateRef = userState.value;

			// Check if the accessor is meant for deletion.
			const isDeletion = mutationFlag === "-";

			for (let i = 0; i < lastElementIndex; i++) {
				const nextStateRef = stateRef?.[accessor[i]];
				if (typeof nextStateRef === "object" && nextStateRef !== null) {
					stateRef = nextStateRef;
				} else if (!isDeletion) {
					// Only create new path elements if it's not a deletion operation.
					stateRef[accessor[i]] = {};
					stateRef = stateRef[accessor[i]];
				}
			}

			if (isDeletion) {
				// If it's a deletion operation, delete the property.
				delete stateRef[accessor.at(-1)];
			} else {
				// Otherwise, set the value as usual.
				stateRef[accessor.at(-1)] = value;
			}
		});
	}

	function ingestComponents(newComponents: Record<string, any>) {
		if (!newComponents) return;
		components.value = newComponents;
	}

	function clearFrontendMap() {
		frontendMessageMap.value.forEach(({ callback }) => {
			callback?.({ ok: false });
		});
		frontendMessageMap.value.clear();
	}

	// Open and setup websocket

	async function startSync(): Promise<void> {
		if (webSocket) return; // Open WebSocket exists

		const logger = useLogger();

		const url = new URL("./api/stream", window.location.href);
		url.protocol = url.protocol.replace("https", "wss");
		url.protocol = url.protocol.replace("http", "ws");
		webSocket = new WebSocket(url.href);

		webSocket.onopen = () => {
			clearFrontendMap();
			syncHealth.value = "connected";
			logger.log("WebSocket connected. Initialising stream...");
			sendFrontendMessage("streamInit", { sessionId });
		};

		webSocket.onmessage = (wsEvent) => {
			const message = JSON.parse(wsEvent.data);

			if (
				message.messageType == "announcement" &&
				message.payload.announce == "codeUpdate"
			) {
				webSocket.close();
				initSession();
				return;
			} else if (
				message.messageType == "eventResponse" ||
				message.messageType == "stateEnquiryResponse"
			) {
				ingestMutations(message.payload?.mutations);
				collateMail(message.payload?.mail);
				ingestComponents(message.payload?.components);
			}

			const mapItem = frontendMessageMap.value.get(message.trackingId);
			mapItem?.callback?.({ ok: true, payload: message.payload });
			frontendMessageMap.value.delete(message.trackingId);
		};

		webSocket.onclose = async (ev: CloseEvent) => {
			webSocket = null;
			syncHealth.value = "offline";

			if (ev.code == 1008) {
				// 1008: Policy Violation
				// Connection established correctly but closed due to invalid session.
				// Do not attempt to reconnect, the session will remain invalid. Initialise a new session.

				logger.error("Invalid session. Reinitialising...");

				// Take care of pending event resolutions and fail them.
				await initSession();
				return;
			}

			// Connection lost due to some other reason. Try to reconnect.

			logger.error("WebSocket closed. Attempting to reconnect...");
			setTimeout(async () => {
				try {
					await startSync();
				} catch {
					logger.error("Couldn't reconnect.");
				}
			}, RECONNECT_DELAY_MS);
		};

		return new Promise((resolve, reject) => {
			webSocket.addEventListener("open", () => resolve(), { once: true });
			webSocket.addEventListener("close", () => reject(), { once: true });
		});
	}

	/**
	 * Dispatches the given mail to the relevant mail subscriptions.
	 * Items that cannot be distributed remain in the inbox.
	 *
	 * @param mail
	 * @returns
	 */
	function collateMail(mail: MailItem[] = []) {
		mailInbox.push(...mail);
		mailInbox = mailInbox.filter((item) => {
			const relevantSubscriptions = mailSubscriptions.filter(
				(ms) => ms.mailType == item.type,
			);

			if (relevantSubscriptions.length == 0) {
				return item;
			}

			relevantSubscriptions.forEach((ms) => ms.fn(item.payload));
		});
	}

	function addMailSubscription(mailType: string, fn: Function) {
		mailSubscriptions.push({ mailType, fn });
		collateMail();
	}

	function getPayloadFromEvent(event: Event) {
		let eventPayload = null;

		if (event instanceof CustomEvent) {
			eventPayload = event.detail?.payload ?? null;
		} else {
			const simplifiedEvent = {};
			for (const i in event) {
				const value = event[i];
				if (typeof value === "function") continue;
				if (value instanceof Object) continue;
				simplifiedEvent[i] = value;
			}
			eventPayload = simplifiedEvent;
		}

		return eventPayload;
	}

	async function forwardEvent(
		event: Event,
		instancePath: InstancePath,
		includeEventPayload: boolean,
	) {
		const eventPayload = includeEventPayload
			? getPayloadFromEvent(event)
			: null;
		let callback: Function;
		let handler: string;

		if (event instanceof CustomEvent) {
			callback = event.detail?.callback;
			handler = event.detail?.handler;
		}

		const messagePayload = async () => ({
			type: event.type,
			instancePath,
			handler,
			payload: await eventPayload,
		});

		sendFrontendMessage("event", messagePayload, callback, true);
	}

	/**
	 * Sends a message to be hashed in the backend using the relevant keys.
	 * Due to security reasons, it works only in edit mode.
	 *
	 * @param message Messaged to be hashed
	 * @returns The hashed message
	 */
	async function hashMessage(message: string): Promise<string> {
		return new Promise((resolve, reject) => {
			const messageCallback = (r: {
				ok: boolean;
				payload?: Record<string, any>;
			}) => {
				if (!r.ok) return reject("Couldn't connect to the server.");
				resolve(r.payload?.message);
			};

			sendFrontendMessage("hashRequest", { message }, messageCallback);
		});
	}

	function updateSourceFile(content: string, path: string[]) {
		const tree = structuredClone(toRaw(sourceFiles.value));
		const node = findSourceFileFromPath(path, tree);
		if (isSourceFilesFile(node)) {
			node.content = content;
			node.complete = true;
			sourceFiles.value = tree;
		}
	}

	async function sendCreateSourceFileRequest(path: string[]): Promise<void> {
		return new Promise((resolve, reject) => {
			const messageCallback = (r: {
				ok: boolean;
				payload?: Record<string, any>;
			}) => {
				if (!r.ok) return reject("Couldn't connect to the server.");
				if (r.payload?.["error"])
					return reject("Couldn't create the file.");

				sourceFiles.value = createFileToSourceFiles(
					path,
					toRaw(sourceFiles.value),
				);
				resolve();
			};

			sendFrontendMessage("createSourceFile", { path }, messageCallback);
		});
	}

	async function sendRenameSourceFileRequest(
		from: string[],
		to: string[],
	): Promise<void> {
		return new Promise((resolve, reject) => {
			const messageCallback = (r: {
				ok: boolean;
				payload?: Record<string, any>;
			}) => {
				if (!r.ok) return reject("Couldn't connect to the server.");
				if (r.payload?.["error"])
					return reject("Couldn't rename the file.");

				sourceFiles.value = moveFileToSourceFiles(
					from,
					to,
					toRaw(sourceFiles.value),
				);
				resolve();
			};

			sendFrontendMessage(
				"renameSourceFile",
				{ from, to },
				messageCallback,
			);
		});
	}

	async function sendDeleteSourceFileRequest(path: string[]): Promise<void> {
		return new Promise((resolve, reject) => {
			const messageCallback = (r: {
				ok: boolean;
				payload?: Record<string, any>;
			}) => {
				if (!r.ok) return reject("Couldn't connect to the server.");
				if (r.payload?.["error"])
					return reject("Couldn't delete the file.");

				sourceFiles.value = deleteFileToSourceFiles(
					path,
					toRaw(sourceFiles.value),
				);
				resolve();
			};

			sendFrontendMessage("deleteSourceFile", { path }, messageCallback);
		});
	}

	async function sendCodeSaveRequest(
		code: string,
		path = ["main.py"],
	): Promise<void> {
		return new Promise((resolve, reject) => {
			const messageCallback = (r: {
				ok: boolean;
				payload?: Record<string, any>;
			}) => {
				if (!r.ok) return reject("Couldn't connect to the server.");
				updateSourceFile(code, path);
				resolve();
			};

			sendFrontendMessage(
				"codeSaveRequest",
				{ code, path },
				messageCallback,
			);

			if (path.join("/") === "main.py") syncHealth.value = "suspended";
		});
	}

	function requestSourceFileLoading(path: string[]): Promise<void> {
		return new Promise((resolve, reject) => {
			const messageCallback = (r: {
				ok: boolean;
				payload?: { content: string };
			}) => {
				if (!r.ok) return reject("Couldn't connect to the server.");

				updateSourceFile(r.payload.content, path);

				resolve();
			};
			sendFrontendMessage("loadSourceFile", { path }, messageCallback);
		});
	}

	async function sendStateEnquiry(callback: Function) {
		sendFrontendMessage("stateEnquiry", {}, callback, true);
	}

	function setupMessageFollowUp(trackingId: number) {
		const INITIAL_FOLLOWUP_MS = 150;
		const SUBSEQUENT_FOLLOWUPS_MS = 150;

		const checkIfStateEnquiryRequired = () => {
			const isPending = frontendMessageMap.value.has(trackingId);
			if (!isPending) return;
			sendStateEnquiry(() =>
				setTimeout(
					checkIfStateEnquiryRequired,
					SUBSEQUENT_FOLLOWUPS_MS,
				),
			);
		};
		setTimeout(checkIfStateEnquiryRequired, INITIAL_FOLLOWUP_MS);
	}

	async function sendFrontendMessage(
		type: string,
		payload: object | (() => Promise<object>),
		callback?: Function,
		track = false,
	) {
		if (syncHealth.value == "offline" || syncHealth.value == "suspended") {
			callback?.({ ok: false });
			return;
		}
		const logger = useLogger();
		const trackingId = frontendMessageCounter++;
		try {
			if (callback || track) {
				frontendMessageMap.value.set(trackingId, {
					callback,
				});
			}
			if (track) {
				setupMessageFollowUp(trackingId);
			}

			let awaitedPayload: object;
			if (typeof payload == "function") {
				awaitedPayload = await payload();
			} else {
				awaitedPayload = payload;
			}

			const wsData = {
				type,
				trackingId,
				payload: awaitedPayload,
			};
			if (webSocket.readyState !== webSocket.OPEN) {
				throw "Connection lost.";
			}
			webSocket.send(JSON.stringify(wsData, bigIntReplacer));
		} catch (error) {
			logger.error("sendFrontendMessage error", error);
			callback?.({ ok: false });
		}
	}

	function deleteComponent(componentId: Component["id"]) {
		delete components.value[componentId];
	}

	function addComponent(component: Component) {
		components.value[component.id] = component;
	}

	/**
	 * Triggers a component update.
	 * @returns
	 */
	async function sendComponentUpdate(): Promise<void> {
		/*
 		Ensure that the backend receives only components 
		created by the frontend (Builder-managed components, BMC), 
		and not the components it generated (Code-managed components, CMC).
 		*/

		const builderManagedComponents = {};

		Object.entries(components.value).forEach(([componentId, component]) => {
			if (component.isCodeManaged) return;
			builderManagedComponents[componentId] = component;
		});

		const payload = {
			components: builderManagedComponents,
		};

		return new Promise((resolve, reject) => {
			const messageCallback = (r: {
				ok: boolean;
				payload?: Record<string, any>;
			}) => {
				if (!r.ok) return reject("Couldn't connect to the server.");
				resolve();
			};
			sendFrontendMessage("componentUpdate", payload, messageCallback);
		});
	}

	function getComponentById(componentId: Component["id"]): Component {
		return components.value[componentId];
	}

	function isChildOf(parentId: Component["id"], childId: Component["id"]) {
		let child = components.value[childId];
		do {
			if (child.parentId == parentId) return true;
			child = components.value[child.parentId];
		} while (child);
		return false;
	}

	/**
	 * Gets registered Writer Framework components.
	 *
	 * @param parentId If specified, only include results that are children of a component with this id.
	 * @param param1 Whether to include Builder-managed components and code-managed components, and whether to sort.
	 * @returns An array of components.
	 */
	function getComponents(
		parentId?: Component["id"],
		{
			includeBMC = true,
			includeCMC = true,
			sortedByPosition = false,
		}: {
			includeBMC?: boolean;
			includeCMC?: boolean;
			sortedByPosition?: boolean;
		} = {},
	): Component[] {
		let ca = Object.values(components.value);

		if (typeof parentId !== "undefined") {
			ca = ca.filter((c) => c.parentId == parentId);
		}

		ca = ca.filter((c) => {
			const isCMC = c.isCodeManaged;
			const isBMC = !isCMC;
			return (includeBMC && isBMC) || (includeCMC && isCMC);
		});

		if (sortedByPosition) {
			ca = ca.sort((a, b) => {
				if (a.isCodeManaged && !b.isCodeManaged) return 1;
				if (!a.isCodeManaged && b.isCodeManaged) return -1;
				return a.position > b.position ? 1 : -1;
			});
		}

		return ca;
	}

	/**
	 * Gets registered Writer Framework components with their child components
	 *
	 * @param parentId If specified, only include results that are children of a component with this id.
	 * @param opts Whether to include Builder-managed components and code-managed components, and whether to sort.
	 * @returns An iterable of components.
	 */
	function* getComponentsNested(
		parentId?: Component["id"],
		opts: {
			includeBMC?: boolean;
			includeCMC?: boolean;
			sortedByPosition?: boolean;
		} = {},
	): Generator<Component> {
		for (const component of getComponents(parentId, opts)) {
			yield component;
			yield* getComponentsNested(component.id, opts);
		}
	}

	function setActivePageFromKey(targetPageKey: string) {
		const pages = getComponents("root");
		const matches = pages.filter((pageComponent) => {
			const pageKey = pageComponent.content["key"];
			return pageKey == targetPageKey;
		});
		if (matches.length == 0) return;
		setActivePageId(matches[0].id);
	}

	function setActivePageId(componentId: Component["id"]) {
		activePageId.value = componentId;
	}

	function getContainableTypes(componentId: Component["id"]) {
		return typeHierarchy.getContainableTypes(components.value, componentId);
	}

	const core = {
		webSocket,
		syncHealth,
		frontendMessageMap: readonly(frontendMessageMap),
		mode: readonly(mode),
		userFunctions: readonly(userFunctions),
		addMailSubscription,
		init,
		forwardEvent,
		hashMessage,
		runCode: readonly(runCode),
		sourceFiles: readonly(sourceFiles),
		sendCodeSaveRequest,
		sendCreateSourceFileRequest,
		sendRenameSourceFileRequest,
		sendDeleteSourceFileRequest,
		requestSourceFileLoading,
		sendComponentUpdate,
		addComponent,
		deleteComponent,
		getComponentById,
		getComponents,
		getComponentsNested,
		setActivePageId,
		activePageId: readonly(activePageId),
		setActivePageFromKey,
		getComponentDefinition,
		getSupportedComponentTypes,
		getContainableTypes,
		sessionTimestamp: readonly(sessionTimestamp),
		userState: readonly(userState),
		isChildOf,
		featureFlags: readonly(featureFlags),
	};

	return core;
}
