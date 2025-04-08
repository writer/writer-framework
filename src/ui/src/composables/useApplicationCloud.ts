import { WriterApi, WriterApiApplicationDeployment } from "@/writerApi";
import { Core } from "@/writerTypes";
import { computed, readonly, ref, shallowRef, watch } from "vue";
import { useLogger } from "./useLogger";
import { useToasts } from "@/builder/useToast";

export function useApplicationCloud(wf: Core) {
	const logger = useLogger();
	const { pushToast } = useToasts();

	const abort = new AbortController();
	const isCloudApp = computed(() => wf.writerApplication.value !== undefined);
	const isDeploying = ref(false);
	const deployError = shallowRef();

	// TODO: define the host
	const apiBaseUrl = "https://app.qordobadev.com/";

	const writerApi = new WriterApi({
		signal: abort.signal,
		baseUrl: apiBaseUrl,
	});
	const deployUrl = computed(
		() =>
			new URL(
				`/aistudio/organization/${wf.writerApplication.value?.organizationId}/agent/${wf.writerApplication.value?.id}/deploy`,
				apiBaseUrl,
			),
	);

	const liveUrl = computed(
		() =>
			deploymentInformation.value.applicationVersionData.data
				?.deploymentUrl,
	);

	const deploymentInformation = shallowRef<
		WriterApiApplicationDeployment | undefined
	>();
	const canDeploy = computed(
		() => isCloudApp.value && deploymentInformation.value !== undefined,
	);

	watch(
		wf.writerApplication,
		() => {
			if (!wf.writerApplication.value) return;
			fetchApplicationDeployment();
		},
		{ immediate: true },
	);

	const hasBeenPublished = computed(() => {
		if (deploymentInformation.value === undefined) return undefined;
		return Boolean(
			deploymentInformation.value.writer &&
				deploymentInformation.value.lastDeployedAt,
		);
	});

	async function fetchApplicationDeployment() {
		if (!wf.writerApplication.value) return;

		deploymentInformation.value =
			await writerApi.fetchApplicationDeployment(
				Number(wf.writerApplication.value.organizationId),
				wf.writerApplication.value.id,
			);
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
			await writerApi.publishApplication(
				Number(wf.writerApplication.value.organizationId),
				wf.writerApplication.value.id,
				{
					applicationVersionId:
						deploymentInformation.value.applicationVersion.id,
					applicationVersionDataId:
						deploymentInformation.value.applicationVersionData.id,
				},
			);
			await fetchApplicationDeployment();
			pushToast({
				type: "success",
				message: "agent deployed",
				action: {
					label: "See it live",
					func: () => {
						console.log(deploymentInformation.value);
						window.open(liveUrl.value, "_blank");
					},
					icon: "open_in_new",
				},
			});
		} catch (e) {
			deployError.value = e;
			logger.error("Deploy failed", e);
			pushToast({ type: "error", message: "deploy failed" });
			// TODO: display error
		} finally {
			isDeploying.value = false;
		}
	}

	return {
		isCloudApp,
		canDeploy,
		hasBeenPublished,
		requestDeployment: publishApplication,
		isDeploying: readonly(isDeploying),
	};
}
