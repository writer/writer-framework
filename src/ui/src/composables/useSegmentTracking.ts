import type { generateCore } from "@/core";
import type {
	AnalyticsBrowser,
	EventProperties,
} from "@segment/analytics-next";
import { useWriterApi } from "./useWriterClient";
import { onMounted, ref } from "vue";
import { WriterApiUserProfile } from "@/writerApi";
import { useLogger } from "./useLogger";

const isIdentified = ref(false);
let fetchUserProfilePromise: Promise<WriterApiUserProfile>;

type SegmentTrackingEventName =
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
	| "ui_block_added"
	| "ui_block_deleted"
	| "ui_blueprint_connected"
	| "ui_block_styles_updated"
	| "blueprints_auto_gen_opened" // ok
	| "blueprints_auto_gen_started" // ok
	| "blueprints_auto_gen_completed" // ok
	| "blueprints_auto_gen_feedback_completed"
	| "blueprints_block_added"
	| "blueprints_block_deleted"
	| "blueprints_run_started" // ok
	| "blueprints_run_failed" // ok
	| "blueprints_run_succeeded" // ok
	| "blueprints_logs_trace_opened"
	| "blueprints_new_added" // ok
	| "blueprints_block_output_copied";

interface WriterEventProperties extends EventProperties {
	componentId?: string;
	componentIds?: string[];
}

// keep only one instance of Segment analytics as promise
const analyticsPromise = (async function getAnalytics() {
	// @ts-expect-error use injected variable from Vite
	if (import.meta.env.MODE === "test") return;

	try {
		window.Q = { CONF: {} };
		// @ts-expect-error import global variable from outside
		await import("/conf/app_conf.js?url");

		// @ts-expect-error use injected variable from Vite
		const writeKey = window.Q.CONF.SEGMENT_ID;
		if (!writeKey) return;

		const module = await import("@segment/analytics-next");
		return module.AnalyticsBrowser.load({ writeKey });
	} catch {
		return null;
	}
})();

async function getAnalytics() {
	const analytics = await analyticsPromise;
	if (!analytics) return;
	return analytics[0];
}

export function useSegmentTracking(wf: ReturnType<typeof generateCore>) {
	const abortControler = new AbortController();

	const { writerApi } = useWriterApi({ signal: abortControler.signal });
	const logger = useLogger();

	// keep only one promise to avoid concurent API call
	if (!fetchUserProfilePromise) {
		fetchUserProfilePromise = writerApi.fetchUserProfile();
	}

	async function getUserId() {
		try {
			const userProfile = await fetchUserProfilePromise;
			return String(userProfile.id);
		} catch {
			return undefined;
		}
	}

	onMounted(async () => {
		const analytics = await getAnalytics();
		if (!analytics) return;

		if (isIdentified.value) return;
		try {
			const userId = await getUserId();
			const userProfile = await fetchUserProfilePromise;
			await analytics.identify(userId, {
				id: userProfile.id,
				email: userProfile.email,
				avatar: userProfile.avatar,
				firstName: userProfile.firstName,
				lastName: userProfile.lastName,
				title: userProfile.jobTitle,
				phone: userProfile.phone,
				createdAt: userProfile.createdAt,
			});
		} catch (e) {
			logger.error(
				"Failed to identify the current user for analytics",
				e,
			);
		} finally {
			isIdentified.value = true;
		}
	});

	type TrackFn = AnalyticsBrowser["track"];

	function enhanceEventProperties(
		properties: WriterEventProperties,
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

	async function track(
		eventName: SegmentTrackingEventName,
		properties: WriterEventProperties = {},
	): ReturnType<TrackFn> {
		if (wf.mode.value !== "edit") return;
		const analytics = await getAnalytics();
		if (!analytics) return;

		const propertiesEnhaced = enhanceEventProperties(properties);
		logger.log(`[track] ${eventName}`, propertiesEnhaced);

		const res = await analytics.track(eventName, propertiesEnhaced, {
			userId: await getUserId(),
		});
		return res;
	}

	async function page(
		category: string,
		name: string,
		properties: WriterEventProperties = {},
	) {
		if (wf.mode.value !== "edit") return;
		const analytics = await getAnalytics();
		if (!analytics) return;

		const propertiesEnhaced = enhanceEventProperties(properties);

		const res = await analytics.page(category, name, propertiesEnhaced, {
			userId: await getUserId(),
		});
		return res;
	}

	function getComponentInformation(componentId: string) {
		const component = wf.getComponentById(componentId);
		if (!component) return {};
		const def = wf.getComponentDefinition(component.type);
		if (!def) return {};
		return { name: def.name, category: def.category };
	}

	return { track, page };
}
