import type { generateCore } from "@/core";
import { useWriterApi } from "./useWriterApi";
import { computed, onMounted } from "vue";
import { useLogger } from "./useLogger";
import { getWriterCloudEnvConfig } from "@/utils/writerCloudEnvConfig";

let isIdentified = false;

type WriterTrackingEventName =
	| "nav_ui_opened"
	| "nav_blueprints_opened"
	| "nav_preview_opened"
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
	let abortControler = new AbortController();

	const logger = useLogger();
	const { writerApi } = useWriterApi({ signal: abortControler.signal });

	async function getFullstoryOrgId() {
		if (!isCloudApp.value) return undefined;
		const config = await getWriterCloudEnvConfig();
		return config["FULLSTORY_ORG_ID"]
			? String(config["FULLSTORY_ORG_ID"])
			: undefined;
	}

	const isCloudApp = computed(() => Boolean(wf.writerApplication.value?.id));
	const organizationId = computed(
		() => Number(wf.writerApplication.value?.organizationId) || undefined,
	);
	const canTrack = computed(
		() => wf.mode.value === "edit" && isCloudApp.value,
	);

	onMounted(async () => {
		abortControler = new AbortController();
		if (!isCloudApp.value || isIdentified) return;
		isIdentified = true;

		try {
			await Promise.all([
				writerApi.analyticsIdentify(),
				initializeFullStory(),
			]);
		} catch (e) {
			logger.error("Failed to setup analytics", e);
		}
	});

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
			writerApplicationId: wf.writerApplication.value?.id,
			writerOrganizationId: wf.writerApplication.value?.organizationId,
			...copy,
		};
	}

	async function initializeFullStory() {
		if (!canTrack.value) return;
		const fullstoryOrgId = await getFullstoryOrgId();
		if (!fullstoryOrgId) return;

		const module = await import("@fullstory/browser");
		if (module.isInitialized()) return;

		await new Promise((res) => {
			module.init(
				{
					orgId: fullstoryOrgId,
				},
				res,
			);
		});

		try {
			const profile = await writerApi.fetchUserProfile();
			await module.FullStory("setIdentityAsync", {
				uid: String(profile.id),
				properties: profile,
			});
		} catch (e) {
			logger.error("Failed to set FullStory identity", e);
		}
	}

	function getComponentInformation(componentId: string) {
		const component = wf.getComponentById(componentId);
		if (!component) return {};
		const def = wf.getComponentDefinition(component.type);
		if (!def) return {};
		return { name: def.name, category: def.category };
	}

	async function trackWithFullStory(
		eventName: string,
		properties: EventProperties,
	) {
		if (!canTrack.value) return;
		const fullstoryOrgId = await getFullstoryOrgId();
		if (!fullstoryOrgId) return;

		const { FullStory } = await import("@fullstory/browser");
		return FullStory("trackEventAsync", { name: eventName, properties });
	}

	function trackWithApi(eventName: string, properties: EventProperties) {
		if (!canTrack.value) return;
		return writerApi.analyticsTrack(eventName, properties);
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
		if (!canTrack.value || !organizationId.value) return;

		return writerApi.analyticsPage(
			`${EVENT_PREFIX} ${name}`,
			organizationId.value,
			expandEventPropertiesWithResources(properties),
		);
	}

	return { track, page };
}
