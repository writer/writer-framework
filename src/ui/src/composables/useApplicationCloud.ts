import { Core } from "@/writerTypes";
import { onBeforeUnmount, onMounted, readonly, ref } from "vue";

const enum IFrameRequestMessage {
	Deploy = "deploy",
}
const enum IFrameResponseMessage {
	DeployStarted = "deployStarted",
	DeployFinished = "deployFinished",
}

export const enum DeploymentStatus {
	Unknown = "unknown",
	InProgress = "inProgress",
	Done = "done",
}

export function useApplicationCloud(wf: Core) {
	const abort = new AbortController();
	const isCloudApp = wf.isCloud;

	onMounted(() => {
		window.addEventListener(
			"message",
			(e) => {
				switch (e.data) {
					case IFrameResponseMessage.DeployStarted:
						deploymentStatus.value = DeploymentStatus.InProgress;
						break;
					case IFrameResponseMessage.DeployFinished:
						deploymentStatus.value = DeploymentStatus.Done;
						break;
				}
			},
			{ signal: abort.signal },
		);
	});

	onBeforeUnmount(abort.abort);

	const deploymentStatus = ref(DeploymentStatus.Unknown);

	function requestDeployment() {
		window.parent.postMessage(IFrameRequestMessage.Deploy, "*");
	}

	return {
		isCloudApp,
		requestDeployment,
		deploymentStatus: readonly(deploymentStatus),
	};
}
