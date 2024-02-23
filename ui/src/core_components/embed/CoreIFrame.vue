<template>
	<ComponentBase ref="rootEl" class="CoreIFrame">
		<iframe :src="fields.src.value" draggable="false" @load="handleLoad" />
	</ComponentBase>
</template>

<script lang="ts">
import { FieldType } from "../../streamsyncTypes";
import { cssClasses } from "../../renderer/sharedStyleFields";

const description = "A component to embed an external resource in an iframe.";

const loadHandlerStub = `
def load_handler(state):

	# Sets status message when resource is loaded

	state["status"] = "Page loaded"`;

export default {
	streamsync: {
		name: "IFrame",
		description,
		category: "Embed",
		fields: {
			src: {
				name: "Source",
				default: "",
				desc: "A valid URL",
				type: FieldType.Text,
			},
			cssClasses,
		},
		events: {
			"ss-load": {
				desc: "Fires when the resource has successfully loaded.",
				stub: loadHandlerStub.trim(),
			},
		},
	},
};
</script>

<script setup lang="ts">
import { Ref, inject, ref } from "vue";
import injectionKeys from "../../injectionKeys";

import ComponentBase from "../../renderer/ComponentBase.vue";

const rootEl: Ref<HTMLElement> = ref(null);
const fields = inject(injectionKeys.evaluatedFields);

function handleLoad() {
	const event = new CustomEvent("ss-load");
	rootEl.value.dispatchEvent(event);
}
</script>

<style scoped>
@import "../../renderer/sharedStyles.css";

.CoreIFrame {
	position: relative;
	width: 100%;
	height: 80vh;
}

.CoreIFrame.beingEdited:not(.selected) iframe {
	pointer-events: none;
}

.CoreIFrame iframe {
	width: 100%;
	height: 100%;
	display: block;
	margin: auto;
	border: 1px solid var(--separatorColor);
}
</style>
