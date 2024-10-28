<template>
	<main
		class="ComponentRenderer"
		tabindex="-1"
		:style="rootStyle"
		:class="{ loadingActive: isMessagePending }"
	>
		<RendererNotifications class="notifications"></RendererNotifications>
		<div class="loadingBar"></div>
		<div class="rootComponentArea">
			<ComponentProxy
				:key="activeRootId"
				:component-id="activeRootId"
				:instance-path="[
					{ componentId: activeRootId, instanceNumber: 0 },
				]"
				:instance-data="[ref(null)]"
			></ComponentProxy>
			<slot></slot>
		</div>
	</main>
</template>

<script setup lang="ts">
import {
	inject,
	ref,
	computed,
	watch,
	ComputedRef,
	onBeforeMount,
	onMounted,
} from "vue";
import { Component } from "@/writerTypes";
import ComponentProxy from "./ComponentProxy.vue";
import RendererNotifications from "./RendererNotifications.vue";
import injectionKeys from "@/injectionKeys";
import { useEvaluator } from "./useEvaluator";
import {
	changePageInHash,
	changeRouteVarsInHash,
	serializeParsedHash,
} from "@/core/navigation";

const wf = inject(injectionKeys.core);
const wfbm = inject(injectionKeys.builderManager);
const templateEvaluator = useEvaluator(wf);
const importedModulesSpecifiers: Record<string, string> = {};

const activeRootId: ComputedRef<Component["id"]> = computed(() => {
	if (!wfbm) return "root";
	if (wfbm.getMode() == "workflows") return "workflows_root";
	return "root";
});

const coreRootFields = templateEvaluator.getEvaluatedFields([
	{ componentId: "root", instanceNumber: 0 },
]);

const rootStyle = computed(() => {
	return {
		"--accentColor": coreRootFields.accentColor?.value,
		"--emptinessColor": coreRootFields.emptinessColor?.value,
		"--containerBackgroundColor":
			coreRootFields.parentIdBackgroundColor?.value,
		"--primaryTextColor": coreRootFields.primaryTextColor?.value,
		"--secondaryTextColor": coreRootFields.secondaryTextColor?.value,
		"--separatorColor": coreRootFields.separatorColor?.value,
	};
});

const isMessagePending = computed(() => wf.frontendMessageMap.value.size > 0);

watch(
	() => coreRootFields.appName?.value,
	(appName: string) => {
		updateTitle(appName);
	},
	{ immediate: true },
);

function updateTitle(appName: string) {
	const mode = wf.mode.value;
	let title: string;
	if (appName && mode == "edit") {
		title = `${appName} | Writer Framework | Builder`;
	} else if (!appName && mode == "edit") {
		title = "Writer Framework | Builder";
	} else if (appName && mode == "run") {
		title = `${appName}`;
	} else if (!appName && mode == "run") {
		title = "Writer Framework App";
	}
	document.title = title;
}

async function importStylesheet(stylesheetKey: string, path: string) {
	const existingEl = document.querySelector(
		`[data-writer-stylesheet-key="${stylesheetKey}"]`,
	);
	existingEl?.remove();
	const el = document.createElement("link");
	el.dataset.writerStylesheetKey = stylesheetKey;
	el.setAttribute("href", path);
	el.setAttribute("rel", "stylesheet");
	document.head.appendChild(el);
}

async function importScript(scriptKey: string, path: string) {
	const existingEl = document.querySelector(
		`[data-writer-script-key="${scriptKey}"]`,
	);
	existingEl?.remove();
	const el = document.createElement("script");
	el.dataset.writerScriptKey = scriptKey;
	el.src = path;
	el.setAttribute("rel", "modulepreload");
	document.head.appendChild(el);
}

async function importModule(moduleKey: string, specifier: string) {
	importedModulesSpecifiers[moduleKey] = specifier;
	await import(/* @vite-ignore */ specifier);
}

async function handleFunctionCall(
	moduleKey: string,
	functionName: string,
	args: unknown[],
) {
	const specifier = importedModulesSpecifiers[moduleKey];
	const m = await import(/* @vite-ignore */ specifier);

	if (!m) {
		// eslint-disable-next-line no-console
		console.warn(
			`The module with key "${moduleKey}" cannot be found. Please check that it has been imported.`,
		);
		return;
	}
	m[functionName](...args);
}

type FileDownloadMailItemPayload = {
	data: string;
	fileName: string;
};

function addMailSubscriptions() {
	wf.addMailSubscription(
		"fileDownload",
		(mailItem: FileDownloadMailItemPayload) => {
			const el = document.createElement("a");
			el.href = mailItem.data;
			el.download = mailItem.fileName;
			el.click();
		},
	);
	wf.addMailSubscription("openUrl", (url: string) => {
		const el = document.createElement("a");
		el.href = url;
		el.target = "_blank";
		el.rel = "noopener noreferrer";
		el.click();
	});
	wf.addMailSubscription("pageChange", (pageKey: string) => {
		changePageInHash(pageKey);
	});
	wf.addMailSubscription(
		"routeVarsChange",
		(routeVars: Record<string, string>) => {
			changeRouteVarsInHash(routeVars);
		},
	);
	wf.addMailSubscription(
		"importStylesheet",
		({ stylesheetKey, path }: { stylesheetKey: string; path: string }) => {
			importStylesheet(stylesheetKey, path);
		},
	);
	wf.addMailSubscription(
		"importScript",
		({ scriptKey, path }: { scriptKey: string; path: string }) => {
			importScript(scriptKey, path);
		},
	);
	wf.addMailSubscription(
		"importModule",
		({
			moduleKey,
			specifier,
		}: {
			moduleKey: string;
			specifier: string;
		}) => {
			importModule(moduleKey, specifier);
		},
	);
	wf.addMailSubscription(
		"functionCall",
		({
			moduleKey,
			functionName,
			args,
		}: {
			moduleKey: string;
			functionName: string;
			args: unknown[];
		}) => {
			handleFunctionCall(moduleKey, functionName, args);
		},
	);
}

function handleAppOpenChange() {
	const parsedHash = serializeParsedHash();
	const event = new CustomEvent("wf-app-open", {
		detail: {
			payload: parsedHash,
		},
	});

	const rootInstance = { componentId: "root", instanceNumber: 0 };
	wf.forwardEvent(event, [rootInstance], true);
}

onBeforeMount(() => {
	addMailSubscriptions();
});

onMounted(() => {
	handleAppOpenChange();
});
</script>

<style scoped>
@import "./sharedStyles.css";

.ComponentRenderer {
	--accentColor: #5551ff;
	--buttonColor: #5551ff;
	--emptinessColor: #ffffff;
	--separatorColor: #e4e7ed;
	--primaryTextColor: #000000;
	--buttonTextColor: #ffffff;
	--secondaryTextColor: #828282;
	--containerBackgroundColor: #ffffff;
	--containerShadow: 0px 2px 0px 0px rgba(0, 0, 0, 0.05);
	width: 100%;
	outline: none;
	--notificationsDisplacement: 0;
	font-family: Poppins, "Helvetica Neue", "Lucida Grande", sans-serif;
	font-size: 0.8rem;
	color: var(--primaryTextColor);
	background: var(--emptinessColor);
	display: flex;
	flex-direction: column;
	min-height: 100%;
	isolation: isolate;
	flex: 1 0 auto;
}
.notifications {
	right: var(--notificationsDisplacement);
}

.loadingBar {
	width: 100%;
	height: 4px;
	margin-bottom: -4px;
	position: sticky;
	top: 0;
	pointer-events: none;
	z-index: 4;
	transition-delay: 0.2s;
	transition-property: opacity;
	transition-duration: 200ms;
	opacity: 0;
}

.loadingActive .loadingBar {
	background-size: 200% 200%;
	opacity: 1;
	animation: loadingAnimation ease-in-out 1s infinite;
	animation-delay: 200ms;
	background-image: linear-gradient(
		270deg,
		var(--emptinessColor),
		var(--accentColor),
		var(--emptinessColor)
	);
}

@keyframes loadingAnimation {
	0% {
		background-position: 0% 0%;
	}
	50% {
		background-position: 100% 100%;
	}
	100% {
		background-position: 0% 0%;
	}
}
.rootComponentArea {
	display: flex;
	flex: 1 0 auto;
}
</style>
