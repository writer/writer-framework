import type { generateCore } from "@/core";
import { useWriterApi } from "./useWriterClient";
import { computed, onMounted, ref } from "vue";
import { useLogger } from "./useLogger";

const isIdentified = ref(false);

type WriterTrackingEventName =
	| "nav_ui_opened" //ok
	| "nav_blueprints_opened" //ok
	| "nav_preview_opened" //ok
	| "nav_deploy_clicked" // ok
	| "nav_logs_opened" // ok
	| "nav_code_opened" // ok
	| "nav_code_file_updated"
	| "deployment_succeeded" // ok
	| "deployment_failed" // ok
	| "nav_state_explorer_opened" // ok
	| "ui_page_added" // ok
	| "ui_block_added" // ok
	| "ui_block_deleted" // ok
	| "ui_blueprint_connected"
	| "ui_block_styles_updated"
	| "blueprints_auto_gen_opened" // ok
	| "blueprints_auto_gen_started" // ok
	| "blueprints_auto_gen_completed" // ok
	| "blueprints_auto_gen_feedback_completed"
	| "blueprints_block_added" // ok
	| "blueprints_block_deleted" // ok
	| "blueprints_run_started" // ok
	| "blueprints_run_failed" // ok
	| "blueprints_run_succeeded" // ok
	| "blueprints_logs_trace_opened"
	| "blueprints_new_added" // ok
	| "blueprints_block_output_copied";

type EventProperties = {
	[key: string]: unknown;
};

interface EventPropertiesWithResources extends EventProperties {
	componentId?: string;
	componentIds?: string[];
}

const EVENT_PREFIX = "[AgentEditor] ";

export function useWriterTracking(wf: ReturnType<typeof generateCore>) {
	const abortControler = new AbortController();

	const isCloudApp = computed(() => wf.writerApplication.value !== undefined);
	const organizationId = computed(
		() => Number(wf.writerApplication.value?.organizationId) || undefined,
	);

	const { writerApi } = useWriterApi({ signal: abortControler.signal });
	const logger = useLogger();

	onMounted(async () => {
		if (!isCloudApp.value || isIdentified.value) return;
		isIdentified.value = true;
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
			writerApplicationId: wf.writerApplication.value?.id,
			writerOrganizationId: wf.writerApplication.value?.organizationId,
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
		if (wf.mode.value !== "edit" || !isCloudApp.value) return;

		const propertiesEnhaced =
			expandEventPropertiesWithResources(properties);

		return writerApi.analyticsTrack(
			`${EVENT_PREFIX} ${eventName}`,
			propertiesEnhaced,
		);
	}

	function page(name: string, properties: EventProperties = {}) {
		if (
			wf.mode.value !== "edit" ||
			!isCloudApp.value ||
			!organizationId.value
		)
			return;

		const propertiesEnhaced =
			expandEventPropertiesWithResources(properties);

		return writerApi.analyticsPage(
			`${EVENT_PREFIX} ${name}`,
			organizationId.value,
			propertiesEnhaced,
		);
	}

	return { track, page };
}
