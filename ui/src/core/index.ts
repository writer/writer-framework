import { ref, Ref } from "vue";
import {
	Component,
	ComponentMap,
	InstancePath,
	MailItem,
} from "../streamsyncTypes";
import {
	getSupportedComponentTypes,
	getComponentDefinition,
} from "./templateMap";
import * as typeHierarchy from "./typeHierarchy";
import { auditAndFixComponents } from "./auditAndFix";
import { parseAccessor } from "./parsing";

const RECONNECT_DELAY_MS = 1000;
const KEEP_ALIVE_DELAY_MS = 60000;

export function generateCore() {
	let sessionId: string = null;
	let mode: Ref<"run" | "edit"> = ref(null);
	let savedCode: Ref<string> = ref(null);
	let runCode: Ref<string> = ref(null);
	const isMessagePending: Ref<boolean> = ref(false);
	const components: Ref<ComponentMap> = ref({});
	const userFunctions: Ref<string[]> = ref([]);
	const userState: Ref<Record<string, any>> = ref({});
	let webSocket: WebSocket;
	const syncHealth: Ref<"idle" | "connected" | "offline"> = ref("idle");
	let frontendMessageCounter = 0;
	const frontendMessageMap: Map<number, { callback?: Function }> = new Map();
	let mailInbox: MailItem[] = [];
	const mailSubscriptions: { mailType: string; fn: Function }[] = [];
	let activePageId: Ref<Component["id"]> = ref(null);

	/**
	 * Whether Streamsync is running as builder or runner.
	 * The mode is enforced in the backend and used in the frontend for presentation purposes only.
	 *
	 * @returns
	 */
	function getMode() {
		return mode.value;
	}

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

		mode.value = initData.mode;
		components.value = initData.components;
		userState.value = initData.userState;
		collateMail(initData.mail);
		sessionId = initData.sessionId;

		// Only returned for edit (Builder) mode

		userFunctions.value = initData.userFunctions;
		savedCode.value = initData.savedCode;
		runCode.value = initData.runCode;

		await startSync();

		if (mode.value != "edit") return;
		const isFixApplied = auditAndFixComponents(initData.components);
		if (!isFixApplied) return;
		await sendComponentUpdate();
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

			const accessor = parseAccessor(key);
			let stateRef = userState.value;
			for (let i = 0; i < accessor.length - 1; i++) {
				let nextStateRef = stateRef?.[accessor[i]];
				if (typeof nextStateRef === "object" && nextStateRef !== null) {
					stateRef = nextStateRef;
				} else {
					stateRef[accessor[i]] = {};
					stateRef = stateRef[accessor[i]];
				}
			}
			stateRef[accessor.at(-1)] = value;
		});
	}

	function clearFrontendMap() {
		frontendMessageMap.forEach(({ callback }) => {
			callback?.({ ok: false });
		});
		frontendMessageMap.clear();
		isMessagePending.value = false;
	}

	// Open and setup websocket

	async function startSync(): Promise<void> {
		if (webSocket) return; // Open WebSocket exists

		const url = new URL("./api/stream", window.location.href);
		url.protocol = url.protocol.replace("https", "wss");
		url.protocol = url.protocol.replace("http", "ws");
		webSocket = new WebSocket(url.href);

		webSocket.onopen = () => {
			clearFrontendMap();
			syncHealth.value = "connected";
			console.log("WebSocket connected. Initialising stream...");
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
			} else if (message.messageType == "eventResponse") {
				ingestMutations(message.payload?.mutations);
				collateMail(message.payload?.mail);
			}

			const mapItem = frontendMessageMap.get(message.trackingId);
			mapItem?.callback?.({ ok: true, payload: message.payload });
			frontendMessageMap.delete(message.trackingId);
			if (frontendMessageMap.size == 0) {
				isMessagePending.value = false;
			}
		};

		webSocket.onclose = async (ev: CloseEvent) => {
			webSocket = null;
			syncHealth.value = "offline";

			if (ev.code == 1008) {
				// 1008: Policy Violation
				// Connection established correctly but closed due to invalid session.
				// Do not attempt to reconnect, the session will remain invalid. Initialise a new session.

				console.error("Invalid session. Reinitialising...");

				// Take care of pending event resolutions and fail them.
				await initSession();
				return;
			}

			// Connection lost due to some other reason. Try to reconnect.

			console.error("WebSocket closed. Attempting to reconnect...");
			setTimeout(async () => {
				try {
					await startSync();
				} catch {
					console.error("Couldn't reconnect.");
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
				(ms) => ms.mailType == item.type
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

	async function forwardEvent(event: Event, instancePath: InstancePath) {
		let eventPayload = null;
		let callback: Function;

		if (event instanceof CustomEvent) {
			eventPayload = event.detail?.payload ?? null;
			callback = event.detail?.callback;
		}

		const messagePayload = async () => ({
			type: event.type,
			instancePath,
			payload: await eventPayload,
		});

		sendFrontendMessage("event", messagePayload, callback, true);
	}

	async function sendCodeSaveRequest(newCode: string): Promise<void> {
		const messageData = {
			code: newCode,
		};

		return new Promise((resolve, reject) => {
			const messageCallback = (r: {
				ok: boolean;
				payload?: Record<string, any>;
			}) => {
				if (!r.ok) {
					reject("Couldn't connect to the server.");
					return;
				}
				resolve();
			};

			sendFrontendMessage(
				"codeSaveRequest",
				messageData,
				messageCallback
			);
		});
	}

	function getSavedCode() {
		return savedCode.value;
	}

	async function sendCodeUpdate(newCode: string): Promise<void> {
		const messageData = {
			code: newCode,
		};

		return new Promise((resolve, reject) => {
			const messageCallback = (r: {
				ok: boolean;
				payload?: Record<string, any>;
			}) => {
				if (!r.ok) {
					reject("Couldn't connect to the server.");
					return;
				}
				resolve();
			};
			sendFrontendMessage("codeUpdate", messageData, messageCallback);
		});
	}

	function getRunCode() {
		return runCode.value;
	}

	async function sendFrontendMessage(
		type: string,
		payload: object | (() => Promise<object>),
		callback?: Function,
		track = false
	) {
		const trackingId = frontendMessageCounter++;
		try {
			if (callback || track) {
				frontendMessageMap.set(trackingId, {
					callback,
				});
				isMessagePending.value = true;
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
			webSocket.send(JSON.stringify(wsData));
		} catch {
			callback?.({ ok: false });
		}
	}

	function deleteComponent(componentId: Component["id"]) {
		// delete renderedComponents[componentId];
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
		const payload = {
			components: components.value,
		};

		return new Promise((resolve, reject) => {
			const messageCallback = (r: {
				ok: boolean;
				payload?: Record<string, any>;
			}) => {
				if (!r.ok) {
					reject("Couldn't connect to the server.");
					return;
				}
				resolve();
			};
			sendFrontendMessage("componentUpdate", payload, messageCallback);
		});
	}

	function getUserFunctions() {
		return userFunctions.value;
	}

	function getBindingValue(componentId: Component["id"]) {
		const component = getComponentById(componentId);
		if (component?.binding?.stateRef) {
			const value = evaluateExpression(component.binding.stateRef);
			return value;
		}
		return;
	}

	function getComponentById(componentId: Component["id"]): Component {
		return components.value[componentId];
	}

	/**
	 * Gets registered Streamsync components.
	 *
	 * @param childrenOfId If specified, only include results that are children of a component with this id.
	 * @param sortedByPosition Whether to sort the components by position or return in random order.
	 * @returns An array of components.
	 */
	function getComponents(
		childrenOfId: Component["id"] = undefined,
		sortedByPosition: boolean = false
	): Component[] {
		let ca = Object.values(components.value);

		if (typeof childrenOfId != "undefined") {
			ca = ca.filter((c) => c.parentId == childrenOfId);
		}
		if (sortedByPosition) {
			ca = ca.sort((a, b) => (a.position > b.position ? 1 : -1));
		}
		return ca;
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

	function getPageKeys() {
		const pages = getComponents("root");
		const pageKeys = pages
			.map((page) => page.content["key"])
			.filter((pageKey) => !!pageKey);
		return pageKeys;
	}

	function setActivePageId(componentId: Component["id"]) {
		activePageId.value = componentId;
	}

	function getActivePageId(): Component["id"] {
		return activePageId.value;
	}

	function getContainableTypes(componentId: Component["id"]) {
		return typeHierarchy.getContainableTypes(components.value, componentId);
	}

	function evaluateExpression(
		expr: string,
		contextData?: Record<string, any>
	) {
		const splitKey = expr.split(".");
		let contextRef = contextData;
		let stateRef = userState.value;

		for (let i = 0; i < splitKey.length; i++) {
			contextRef = contextRef?.[splitKey[i]];
			stateRef = stateRef?.[splitKey[i]];
		}

		return contextRef ?? stateRef;
	}

	const core = {
		webSocket,
		syncHealth,
		isMessagePending,
		getMode,
		getUserFunctions,
		addMailSubscription,
		init,
		evaluateExpression,
		forwardEvent,
		getSavedCode,
		getRunCode,
		sendCodeSaveRequest,
		sendCodeUpdate,
		sendComponentUpdate,
		addComponent,
		deleteComponent,
		getBindingValue,
		getComponentById,
		getComponents,
		setActivePageId,
		getActivePageId,
		getPageKeys,
		setActivePageFromKey,
		getComponentDefinition,
		getSupportedComponentTypes,
		getContainableTypes,
	};

	return core;
}
