import { WriterApiApplicationDeployment } from "@/writerApi";
import { Core } from "@/writerTypes";
import { computed, onMounted, readonly, ref, shallowRef, watch } from "vue";
import { useToasts } from "@/builder/useToast";
import { useLogger } from "@/composables/useLogger";
import { useWriterApi } from "@/composables/useWriterApi";
import { useWriterTracking } from "@/composables/useWriterTracking";
import { useDebouncer } from "@/composables/useDebouncer";
import { useAbortController } from "@/composables/useAbortController";

export function useWriterAppDeployment(wf: Core) {
	const abort = useAbortController();

	const tracking = useWriterTracking(wf);

	const logger = useLogger();
	const { pushToast } = useToasts();
	const { writerApi, apiBaseUrl } = useWriterApi({ signal: abort.signal });

	const root = computed(() => wf.getComponentById("root"));
	const isDeploying = ref(false);
	const deployError = shallowRef();
	const deploymentInformation = shallowRef<
		WriterApiApplicationDeployment | undefined
	>();

	const updateAppName = useDebouncer(async () => {
		if (
			wf.isWriterCloudApp.value &&
			wf.mode.value === "edit" &&
			!lastDeployedAt.value
		) {
			writerApi.updateApplicationMetadata(
				wf.writerOrgId.value,
				wf.writerAppId.value,
				{
					name: name.value,
				},
			);
		}
		await wf.sendComponentUpdate();
	}, 1_000);

	const name = computed<string>({
		get: () => {
			return root.value.content["appName"];
		},
		set: (value) => {
			if (root.value.content["appName"] === value) return;
			root.value.content["appName"] = value;
			updateAppName();
		},
	});

	watch(() => root.value.content["appName"], updateAppName);
	watch(deploymentInformation, () => {
		const deployName = deploymentInformation.value?.name;

		if (deployName === undefined) return;
		name.value = deployName;
	});

	const liveUrl = computed(() => {
		const teamId = deploymentInformation.value.writer?.teamIds?.[0];
		if (!teamId) return undefined;
		const path = `/organization/${wf.writerOrgId.value}/team/${teamId}/framework/${wf.writerAppId.value}`;
		return new URL(path, apiBaseUrl);
	});

	const writerDeployUrl = computed(() => {
		if (!wf.writerOrgId.value || !wf.writerAppId.value) return;
		return new URL(
			`/aistudio/organization/${wf.writerOrgId.value}/agent/${wf.writerAppId.value}/deploy`,
			apiBaseUrl,
		);
	});

	const lastDeployedAt = computed(() => {
		return deploymentInformation.value?.lastDeployedAt
			? new Date(deploymentInformation.value.lastDeployedAt)
			: undefined;
	});

	const canDeploy = computed(() =>
		Boolean(wf.isWriterCloudApp.value && deploymentInformation.value),
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
					wf.writerOrgId.value,
					wf.writerAppId.value,
				);
		} catch (e) {
			logger.error("Failed to fetch deployment information", e);
			deploymentInformation.value = undefined;
		}
	}

	async function publishApplication() {
		if (!wf.writerApplication.value) return;

		if (!hasBeenPublished.value) {
			const path = `/aistudio/organization/${wf.writerOrgId.value}/agent/${wf.writerAppId.value}/deploy`;
			const deployUrl = new URL(path, apiBaseUrl);
			window.open(deployUrl, "_blank");
			return;
		}

		isDeploying.value = true;
		deployError.value = undefined;

		try {
			await writerApi.publishApplication(
				wf.writerOrgId.value,
				wf.writerAppId.value,
				{
					applicationVersionId:
						deploymentInformation.value.applicationVersion.id,
					applicationVersionDataId:
						deploymentInformation.value.applicationVersionData.id,
				},
			);
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

	return {
		name,
		canDeploy,
		writerDeployUrl,
		hasBeenPublished,
		publishApplication,
		isDeploying: readonly(isDeploying),
		lastDeployedAt,
	};
}
