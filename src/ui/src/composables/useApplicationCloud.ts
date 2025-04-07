import { WriterApi, WriterApiApplicationDeployment } from "@/writerApi";
import { Core } from "@/writerTypes";
import { computed, readonly, ref, shallowRef, watch } from "vue";

export const enum DeploymentStatus {
	Unknown = "unknown",
	InProgress = "inProgress",
	Done = "done",
}

export function useApplicationCloud(wf: Core) {
	const abort = new AbortController();
	const isCloudApp = computed(() => wf.writerApplication.value !== undefined);

	const writerApi = new WriterApi({
		signal: abort.signal,
		// TODO: remove this
		baseUrl: "https://app.qordobadev.com/",
	});

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
		return (
			deploymentInformation.value.writer !== undefined &&
			deploymentInformation.value.lastDeployedAt !== undefined
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
		deploymentStatus.value = DeploymentStatus.InProgress;
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
			deploymentStatus.value = DeploymentStatus.Done;
		} catch (e) {
			// TODO: display error
		}
	}

	const deploymentStatus = ref(DeploymentStatus.Unknown);

	return {
		isCloudApp,
		canDeploy,
		hasBeenPublished,
		requestDeployment: publishApplication,
		deploymentStatus: readonly(deploymentStatus),
	};
}
