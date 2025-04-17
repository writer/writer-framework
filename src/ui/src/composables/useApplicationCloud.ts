import { WriterApi, WriterApiApplicationDeployment } from "@/writerApi";
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
import { useDebouncer } from "./useDebouncer";

export function useApplicationCloud(wf: Core) {
	const logger = useLogger();
	const { pushToast } = useToasts();

	const abort = new AbortController();

	const isDeploying = ref(false);
	const deployError = shallowRef();
	const deploymentInformation = shallowRef<
		WriterApiApplicationDeployment | undefined
	>();

	const root = computed(() => wf.getComponentById("root"));

	const updateAppName = useDebouncer(async () => {
		if (isCloudApp.value && wf.mode.value === "edit") {
			writerApi.updateApplicationMetadata(orgId.value, appId.value, {
				name: name.value,
			});
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

	const apiBaseUrl =
		// @ts-expect-error use injected variable from Vite to specify the host on local env
		import.meta.env.VITE_WRITER_BASE_URL ?? window.location.origin;

	const writerApi = new WriterApi({
		signal: abort.signal,
		baseUrl: apiBaseUrl,
	});

	const isCloudApp = computed(() => Boolean(wf.writerApplication.value));
	const orgId = computed(() => {
		return Number(wf.writerApplication.value?.organizationId) || undefined;
	});
	const appId = computed(() => wf.writerApplication.value?.id);

	const writerDeployUrl = computed(() => {
		return new URL(
			`/aistudio/organization/${orgId.value}/agent/${appId.value}/deploy`,
			apiBaseUrl,
		);
	});

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
		if (!wf.writerApplication.value || wf.mode.value !== "edit") return;

		if (!hasBeenPublished.value) {
			window.open(writerDeployUrl.value, "_blank");
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
		} catch (e) {
			deployError.value = e;
			logger.error("Deploy failed", e);
			pushToast({ type: "error", message: "deploy failed" });
		} finally {
			isDeploying.value = false;
		}
	}

	onUnmounted(() => abort.abort());

	return {
		writerDeployUrl,
		name,
		isCloudApp,
		canDeploy,
		hasBeenPublished,
		publishApplication,
		isDeploying: readonly(isDeploying),
		lastDeployedAt,
	};
}
