<template>
	<div ref="rootEl" class="CoreWebcamCapture">
		<div v-show="isActive" class="main">
			<video ref="videoEl" autoplay="true"></video>
		</div>
		<div class="actions">
			<WdsButton v-if="refreshRate == 0" @click="sendFrame">
				Capture image
			</WdsButton>

			<WdsButton @click="toggleActive">
				{{ isActive ? "Stop capture" : "Start webcam capture" }}
			</WdsButton>
			<WdsDropdownInput
				v-if="videoDevices?.length > 1"
				v-model="preferredDeviceId"
			>
				<option
					v-for="(device, deviceIndex) in videoDevices"
					:key="device.deviceId"
					:value="device.deviceId"
				>
					{{ device.label || `Webcam ${deviceIndex + 1}` }}
				</option>
			</WdsDropdownInput>
		</div>
	</div>
</template>

<script lang="ts">
import { FieldType } from "@/writerTypes";
import {
	buttonColor,
	buttonShadow,
	buttonTextColor,
	cssClasses,
	separatorColor,
} from "@/renderer/sharedStyleFields";
import WdsButton from "@/wds/WdsButton.vue";
import WdsDropdownInput from "@/wds/WdsDropdownInput.vue";
import { useLogger } from "@/composables/useLogger";
import { validatorPositiveNumber } from "@/constants/validators";

const description =
	"A user input component that allows users to capture images using their webcam.";

const ssWebcamHandlerStub = `
def webcam_handler(payload):

	# This handler will save the captured images based on timestamp

	import time
	timestamp = time.time()

	# The payload is a file-like object which contains the captured image
	# in PNG format

	image_file = payload
	with open(f"capture-{timestamp}.png", "wb") as file_handle:
		file_handle.write(image_file)`.trim();

export default {
	writer: {
		name: "Webcam Capture",
		description,
		category: "Other",
		fields: {
			refreshRate: {
				name: "Refresh rate (ms)",
				init: "200",
				default: "200",
				desc: "Set to 0 for manual capture.",
				type: FieldType.Number,
				validator: validatorPositiveNumber,
			},
			buttonColor,
			buttonTextColor,
			buttonShadow,
			separatorColor,
			cssClasses,
		},
		events: {
			"wf-webcam": {
				desc: "Sent when a frame is captured. Its payload contains the captured frame in PNG format.",
				stub: ssWebcamHandlerStub.trim(),
				eventPayloadExample: "data:image/png;base64,azerty",
			},
		},
	},
};
</script>

<script setup lang="ts">
import {
	computed,
	inject,
	onBeforeUnmount,
	onMounted,
	Ref,
	ref,
	useTemplateRef,
	watch,
} from "vue";
import injectionKeys from "@/injectionKeys";

const isActive = ref(false);
const rootEl = useTemplateRef("rootEl");
const canvasEl = document.createElement("canvas");
const videoEl = useTemplateRef("videoEl");
const fields = inject(injectionKeys.evaluatedFields);
const videoDevices: Ref<MediaDeviceInfo[]> = ref(null);
const preferredDeviceId: Ref<MediaDeviceInfo["deviceId"]> = ref(null);

const logger = useLogger();

onMounted(async () => {
	videoDevices.value = await getVideoDevices();
	preferredDeviceId.value = videoDevices.value?.[0]?.deviceId;
});

onBeforeUnmount(() => {
	stopCapture();
});

const getVideoDevices = async () => {
	const devices = await navigator.mediaDevices.enumerateDevices();
	const videoDevices = devices.filter((d) => d.kind == "videoinput");
	return videoDevices;
};

const refreshRate = computed(() => {
	return fields.refreshRate.value;
});

watch(refreshRate, (newRate, prevRate) => {
	if (newRate > 0 && prevRate <= 0) {
		sendFrame();
	}
});

watch(preferredDeviceId, async () => {
	if (!isActive.value) return;
	stopCapture();
	await startCapture();
});

const toggleActive = async () => {
	isActive.value = !isActive.value;
	if (!isActive.value) {
		stopCapture();
		return;
	}
	await startCapture();
	sendFrame();
};

const getFrameAsDataURL = () => {
	const context = canvasEl.getContext("2d");
	context.drawImage(videoEl.value, 0, 0);
	const dataURL = canvasEl.toDataURL("image/png");
	return dataURL;
};

const sendFrame = () => {
	const event = new CustomEvent("wf-webcam", {
		detail: {
			payload: getFrameAsDataURL(),
			callback: () => {
				if (refreshRate.value <= 0 || !isActive.value) return;
				setTimeout(() => {
					sendFrame();
				}, refreshRate.value);
			},
		},
	});

	rootEl.value.dispatchEvent(event);
};

const startCapture = async (): Promise<void> => {
	videoEl.value.style.display = "";
	return new Promise((resolve, reject) => {
		if (!navigator.mediaDevices.getUserMedia) {
			logger.error("This browser doesn't support webcam connection.");
			reject();
		}

		const constraints: MediaStreamConstraints = { video: true };
		if (videoDevices.value.length > 1) {
			constraints.video = {
				deviceId: preferredDeviceId.value,
			};
		}

		navigator.mediaDevices
			.getUserMedia(constraints)
			.then((stream) => {
				videoEl.value.srcObject = stream;
				const webcamWidth = stream
					.getVideoTracks()[0]
					.getSettings().width;
				const webcamHeight = stream
					.getVideoTracks()[0]
					.getSettings().height;
				canvasEl.setAttribute("width", webcamWidth.toString());
				canvasEl.setAttribute("height", webcamHeight.toString());
				resolve();
			})
			.catch((error) => {
				logger.error(
					"An error occurred when trying to use the webcam.",
					error,
				);
				reject();
			});
	});
};

const stopCapture = () => {
	const stream = videoEl.value.srcObject as MediaStream;

	if (stream) {
		const tracks = stream.getTracks();
		tracks.map((track) => track.stop());
	}

	videoEl.value.srcObject = null;
	videoEl.value.style.display = "none";
};
</script>

<style scoped>
@import "@/renderer/sharedStyles.css";
@import "@/renderer/colorTransformations.css";

.CoreWebcamCapture {
	width: 100%;
}

video {
	width: 100%;
	max-width: 70ch;
	margin-bottom: 16px;
}

.actions {
	display: flex;
	gap: 16px;
}
</style>
