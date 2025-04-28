import { WriterApiApplicationDeployment } from "@/writerApi";
import { Core } from "@/writerTypes";
import {
	computed,
	onMounted,
	onUnmounted,
	readonly,
	ref,
	shallowRef,
	watch,
} from "vue";
import { useLogger } from "./useLogger";
import { useToasts } from "@/builder/useToast";
import { useWriterApi } from "./useWriterApi";
import { useWriterTracking } from "./useWriterTracking";

export function useApplicationCloud(wf: Core) {
	const abort = new AbortController();

	const tracking = useWriterTracking(wf);

	const logger = useLogger();
	const { pushToast } = useToasts();
	const { writerApi, apiBaseUrl } = useWriterApi({ signal: abort.signal });

	const isDeploying = ref(false);
	const deployError = shallowRef();
	const deploymentInformation = shallowRef<
		WriterApiApplicationDeployment | undefined
	>();

	const isCloudApp = computed(() => wf.writerApplication.value !== undefined);
	const orgId = computed(() => {
		return Number(wf.writerApplication.value?.organizationId) || undefined;
	});
	const appId = computed(() => wf.writerApplication.value?.id);

	const liveUrl = computed(() => {
		const teamId = deploymentInformation.value.writer?.teamIds?.[0];
		if (!teamId) return undefined;
		const path = `/organization/${orgId.value}/team/${teamId}/framework/${appId.value}`;
		return new URL(path, apiBaseUrl);
	});

	const lastDeployedAt = computed(() => {
		return deploymentInformation.value.lastDeployedAt
			? new Date(deploymentInformation.value.lastDeployedAt)
			: undefined;
	});

	const canDeploy = computed(() =>
		Boolean(isCloudApp.value && deploymentInformation.value),
	);

	const hasBeenPublished = computed(() => {
		return deploymentInformation.value?.status === "deployed";
	});

	watch(wf.writerApplication, fetchApplicationDeployment, {
		immediate: true,
	});

	onMounted(() => {
		// refresh deployment status when user navigates back to the tab
		document.addEventListener(
			"visibilitychange",
			async () => {
				if (document.visibilityState === "visible") {
					await fetchApplicationDeployment();
				}
			},
			{ signal: abort.signal },
		);
	});

	async function fetchApplicationDeployment() {
		if (!wf.writerApplication.value) return;

		try {
			deploymentInformation.value =
				await writerApi.fetchApplicationDeployment(
					orgId.value,
					appId.value,
				);
		} catch (e) {
			logger.error("Failed to fetch deployment information", e);
			deploymentInformation.value = undefined;
		}
	}

	async function publishApplication() {
		if (!wf.writerApplication.value) return;

		if (!hasBeenPublished.value) {
			const path = `/aistudio/organization/${orgId.value}/agent/${appId.value}/deploy`;
			const deployUrl = new URL(path, apiBaseUrl);
			window.open(deployUrl, "_blank");
			return;
		}

		isDeploying.value = true;
		deployError.value = undefined;

		try {
			await writerApi.publishApplication(orgId.value, appId.value, {
				applicationVersionId:
					deploymentInformation.value.applicationVersion.id,
				applicationVersionDataId:
					deploymentInformation.value.applicationVersionData.id,
			});
			await fetchApplicationDeployment();
			const action = liveUrl.value
				? {
						label: "See it live",
						func: () => window.open(liveUrl.value, "_blank"),
						icon: "open_in_new",
					}
				: undefined;
			pushToast({ type: "success", message: "agent deployed", action });

			tracking.track("deployment_succeeded");
		} catch (e) {
			tracking.track("deployment_failed", { error: String(e) });
			deployError.value = e;
			logger.error("Deploy failed", e);
			pushToast({ type: "error", message: "deploy failed" });
		} finally {
			isDeploying.value = false;
		}
	}

	onUnmounted(() => abort.abort());

	return {
		isCloudApp,
		canDeploy,
		hasBeenPublished,
		publishApplication,
		isDeploying: readonly(isDeploying),
		lastDeployedAt,
	};
}
