import type { generateCore } from "@/core";
import { useWriterApi } from "./useWriterApi";
import { watch } from "vue";
import { useLogger } from "./useLogger";

let isIdentified = false;

type WriterTrackingEventName =
	| "nav_export_clicked"
	| "nav_import_clicked"
	| "nav_ui_opened"
	| "nav_blueprints_opened"
	| "nav_preview_opened"
	| "nav_vault_opened"
	| "nav_deploy_clicked"
	| "nav_logs_opened"
	| "nav_code_opened"
	| "nav_code_file_updated"
	| "deployment_succeeded"
	| "deployment_failed"
	| "nav_state_explorer_opened"
	| "ui_page_added"
	| "ui_block_added"
	| "ui_block_deleted"
	| "ui_blueprint_connected"
	| "ui_block_styles_updated"
	| "blueprints_auto_gen_opened"
	| "blueprints_auto_gen_started"
	| "blueprints_auto_gen_completed"
	| "blueprints_auto_gen_feedback_completed"
	| "blueprints_block_added"
	| "blueprints_block_deleted"
	| "blueprints_run_started"
	| "blueprints_run_failed"
	| "blueprints_run_succeeded"
	| "blueprints_logs_trace_opened"
	| "blueprints_new_added"
	| "blueprints_block_output_copied";

type EventProperties = {
	[key: string]: unknown;
};

interface EventPropertiesWithResources extends EventProperties {
	componentId?: string;
	componentIds?: string[];
}

const EVENT_PREFIX = "[AgentEditor]";

export function useWriterTracking(wf: ReturnType<typeof generateCore>) {
	const abortControler = new AbortController();

	const logger = useLogger();
	const { writerApi } = useWriterApi({ signal: abortControler.signal });

	const canTrack = wf.isWriterCloudApp;

	if (!isIdentified) {
		const stop = watch(
			canTrack,
			async () => {
				if (isIdentified || !canTrack.value) return;
				isIdentified = true;
				try {
					const fetchUserProfile = writerApi.fetchUserProfile();
					await Promise.allSettled([
						writerApi.analyticsIdentify(),
						initializeChameleon(fetchUserProfile),
						initializeFullStory(fetchUserProfile),
					]);
				} catch (e) {
					logger.error(
						"Failed to identify the current user for analytics",
						e,
					);
				} finally {
					stop();
				}
			},
			{ immediate: true },
		);
	}

	async function initializeChameleon(
		fetchUserProfile = writerApi.fetchUserProfile(),
	) {
		if (wf.mode.value === "run") return;
		const chameleon = await import("@chamaeleonidae/chmln");
		chameleon.init(
			"S6dr31v4MO4wuteztVhxysLkoA9HsZ6HnDaOTDLqNXHYZq-1P02ek-E3BR4Zgv4pMwdoYO",
			{
				fastUrl: "https://fast.chameleon.io/",
			},
		);
		const profile = await fetchUserProfile;
		chameleon.identify(profile.id, {
			email: profile?.email,
			name:
				profile?.fullName ??
				`${profile?.firstName} ${profile.lastName}`,
		});
	}

	async function initializeFullStory(
		fetchUserProfile = writerApi.fetchUserProfile(),
	) {
		if (!canTrack.value) return;

		const module = await import("@fullstory/browser");
		if (module.isInitialized()) return;

		module.init({
			orgId: "o-2316W7-na1",
			devMode: import.meta.env.DEV,
		});

		try {
			const profile = await fetchUserProfile;
			await module.FullStory("setIdentityAsync", {
				uid: `segment-prefix-${profile.id}`,
				properties: profile,
				consent: true,
			});
		} catch (e) {
			logger.error("Failed to set FullStory identity", e);
		}
	}

	async function trackWithFullStory(
		eventName: string,
		properties: EventProperties,
	) {
		if (!canTrack.value) return;

		const { FullStory } = await import("@fullstory/browser");
		return FullStory("trackEventAsync", { name: eventName, properties });
	}

	function trackWithApi(eventName: string, properties: EventProperties) {
		if (!canTrack.value) return;
		return writerApi.analyticsTrack(eventName, properties);
	}

	function getComponentInformation(componentId: string) {
		const component = wf.getComponentById(componentId);
		if (!component) return {};
		const def = wf.getComponentDefinition(component.type);
		if (!def) return {};
		return { name: def.name, category: def.category };
	}

	function expandEventPropertiesWithResources(
		properties: EventPropertiesWithResources,
	): EventProperties {
		const copy = structuredClone(properties);

		if (typeof copy.componentId === "string") {
			copy.component = getComponentInformation(copy.componentId);
			delete copy.componentId;
		}
		if (Array.isArray(copy.componentIds)) {
			copy.components = copy.componentIds.map(getComponentInformation);
			delete copy.componentIds;
		}

		return {
			writerApplicationId: wf.writerAppId.value,
			writerOrganizationId: String(wf.writerOrgId.value),
			...copy,
		};
	}

	async function track(
		eventName: WriterTrackingEventName,
		properties: EventProperties = {},
	) {
		if (!canTrack.value) return;

		const eventNameFormated = `${EVENT_PREFIX} ${eventName}`;
		const propertiesExpanded =
			expandEventPropertiesWithResources(properties);
		logger.log("[tracking]", eventNameFormated, propertiesExpanded);

		return await Promise.all([
			trackWithApi(eventNameFormated, propertiesExpanded),
			trackWithFullStory(eventNameFormated, propertiesExpanded),
		]).catch(logger.error);
	}

	function page(name: string, properties: EventProperties = {}) {
		if (!canTrack.value) return;
		if (!wf.writerOrgId.value) {
			return;
		}

		return writerApi.analyticsPage(
			`${EVENT_PREFIX} ${name}`,
			wf.writerOrgId.value,
			expandEventPropertiesWithResources(properties),
		);
	}

	return { track, page };
}
