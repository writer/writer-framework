import type { generateCore } from "@/core";
import { useWriterApi } from "./useWriterApi";
import { onMounted } from "vue";
import { useLogger } from "./useLogger";

let isIdentified = false;

type WriterTrackingEventName =
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

	const { writerApi } = useWriterApi({ signal: abortControler.signal });
	const logger = useLogger();

	onMounted(async () => {
		if (!wf.isWriterCloudApp || isIdentified) return;
		isIdentified = true;
		try {
			await writerApi.analyticsIdentify();
		} catch (e) {
			logger.error(
				"Failed to identify the current user for analytics",
				e,
			);
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
			writerApplicationId: wf.writerAppId.value,
			writerOrganizationId: String(wf.writerOrgId.value),
			...copy,
		};
	}

	function getComponentInformation(componentId: string) {
		const component = wf.getComponentById(componentId);
		if (!component) return {};
		const def = wf.getComponentDefinition(component.type);
		if (!def) return {};
		return { name: def.name, category: def.category };
	}

	function track(
		eventName: WriterTrackingEventName,
		properties: EventProperties = {},
	) {
		if (wf.mode.value !== "edit" || !wf.isWriterCloudApp.value) return;

		return writerApi.analyticsTrack(
			`${EVENT_PREFIX} ${eventName}`,
			expandEventPropertiesWithResources(properties),
		);
	}

	function page(name: string, properties: EventProperties = {}) {
		if (
			wf.mode.value !== "edit" ||
			!wf.isWriterCloudApp.value ||
			!wf.writerOrgId.value
		) {
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
