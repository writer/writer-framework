import { WriterApi, WriterApiApplicationDeployment } from "@/writerApi";
import { Core } from "@/writerTypes";
import { computed, onMounted, readonly, ref, shallowRef, watch } from "vue";
import { useLogger } from "./useLogger";
import { useToasts } from "@/builder/useToast";

export function useApplicationCloud(wf: Core) {
	const logger = useLogger();
	const { pushToast } = useToasts();

	const abort = new AbortController();

	const isDeploying = ref(false);
	const deployError = shallowRef();
	const deploymentInformation = shallowRef<
		WriterApiApplicationDeployment | undefined
	>();

	const apiBaseUrl =
		// @ts-expect-error use injected variable from Vite to specify the host on local env
		import.meta.env.VITE_WRITER_BASE_URL ?? window.location.origin;

	const writerApi = new WriterApi({
		signal: abort.signal,
		baseUrl: apiBaseUrl,
	});

	const isCloudApp = computed(() => wf.writerApplication.value !== undefined);
	const orgId = computed(() => {
		return Number(wf.writerApplication.value?.organizationId) || undefined;
	});
	const appId = computed(() => wf.writerApplication.value?.id);

	const deployUrl = computed(() => {
		return new URL(
			`/aistudio/organization/${orgId.value}/agent/${appId.value}/deploy`,
			apiBaseUrl,
		);
	});

	const liveUrl = computed(() => {
		return deploymentInformation.value.applicationVersionData.data
			?.deploymentUrl;
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
		if (deploymentInformation.value === undefined) return undefined;
		return Boolean(
			deploymentInformation.value.writer &&
				deploymentInformation.value.lastDeployedAt,
		);
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
			window.open(deployUrl.value, "_blank");
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
			pushToast({
				type: "success",
				message: "agent deployed",
				action: {
					label: "See it live",
					func: () => window.open(liveUrl.value, "_blank"),
					icon: "open_in_new",
				},
			});
		} catch (e) {
			deployError.value = e;
			logger.error("Deploy failed", e);
			pushToast({ type: "error", message: "deploy failed" });
		} finally {
			isDeploying.value = false;
		}
	}

	return {
		isCloudApp,
		canDeploy,
		hasBeenPublished,
		publishApplication,
		isDeploying: readonly(isDeploying),
		lastDeployedAt,
	};
}
