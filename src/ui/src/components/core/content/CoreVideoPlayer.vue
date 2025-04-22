<docs lang="md">
Use your app's static folder to serve videos directly. For example, \`static/my_video.mp4\`.

Alternatively, you can pack bytes or files in state:

\`state["vid_b"] = wf.pack_bytes(vid_bytes, "video/mp4")\`

\`state["vid_f"] = wf.pack_file(vid_file, "video/mp4")\`

Afterwards, you can reference the video using the syntax \`@{vid_f}\`.
</docs>

<template>
	<div class="CoreVideoPlayer">
		<video
			:src="fields.src.value"
			:controls="fields.controls.value"
			:autoplay="fields.autoplay.value"
			:loop="fields.loop.value"
			:muted="fields.muted.value"
		></video>
		<div class="mask" />
	</div>
</template>

<script lang="ts">
import { FieldType } from "@/writerTypes";
import { validatorUri } from "@/constants/validators";
import { baseYesNoField, cssClasses } from "@/renderer/sharedStyleFields";

const description =
	"A video player component that can play various video formats.";

export default {
	writer: {
		name: "Video player",
		description,
		category: "Content",
		fields: {
			src: {
				name: "Source",
				desc: "The URL of the video file. Alternatively, you can pass a file via state.",
				default: "",
				type: FieldType.Text,
				validator: validatorUri,
			},
			controls: {
				...baseYesNoField,
				name: "Controls",
				desc: "Display video player controls.",
				default: "yes",
			},
			autoplay: {
				...baseYesNoField,
				name: "Autoplay",
				desc: "Autoplay the video when the component is loaded.",
				default: "no",
			},
			loop: {
				...baseYesNoField,
				name: "Loop",
				desc: "Loop the video when it reaches the end.",
				default: "no",
			},
			muted: {
				...baseYesNoField,
				name: "Muted",
				desc: "Mute the video by default.",
				default: "no",
			},
			cssClasses,
		},
	},
};
</script>

<script setup lang="ts">
import { inject } from "vue";
import injectionKeys from "@/injectionKeys";

const fields = inject(injectionKeys.evaluatedFields);
</script>

<style scoped>
.CoreVideoPlayer {
	position: relative;
	width: 100%;
}

video {
	width: 100%;
}

.mask {
	pointer-events: none;
}

.beingEdited .mask {
	pointer-events: auto;
	position: absolute;
	top: 0;
	left: 0;
	width: 100%;
	height: 100%;
	background-color: rgba(0, 0, 0, 0);
}

.beingEdited.selected .mask {
	pointer-events: none;
}
</style>
