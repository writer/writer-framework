<template>
	<div class="CoreIFrame" v-on:click="handleClick" ref="rootEl">
		<iframe
      @load="handleLoad" 
			:src="fields.src.value"
			draggable="false"
		/>
    <div class="mask" />
	</div>
</template>

<script lang="ts">
import { FieldCategory, FieldType } from "../streamsyncTypes";
import { cssClasses, secondaryTextColor } from "../renderer/sharedStyleFields";
import { getClick } from "../renderer/syntheticEvents";

const description = "A component to embed an external resource in an iframe.";

const loadHandlerStub = `
def load_handler(state):

	# Sets status message when resource is loaded

	state["status"] = "Page loaded"`;

export default {
	streamsync: {
		name: "IFrame",
		description,
		category: "Content",
		fields: {
			src: {
				name: "Source",
				default: '',
				desc: "A valid URL. Alternatively, you can provide a state reference to a Matplotlib figure or a packed file.",
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
import { Ref, computed, inject, ref } from "vue";
import injectionKeys from "../injectionKeys";

const rootEl:Ref<HTMLElement> = ref(null); 
const fields = inject(injectionKeys.evaluatedFields);

function handleClick(ev: MouseEvent) {
	const ssEv = getClick(ev);
	rootEl.value.dispatchEvent(ssEv);
}
function handleLoad(ev) {
	const event = new CustomEvent("ss-load");
	rootEl.value.dispatchEvent(event);
}
</script>

<style scoped>
@import "../renderer/sharedStyles.css";

.CoreIFrame {
  position: relative;
  width: 100%;
  height: 80vh;
}

.CoreIFrame  iframe {
  width: 100%;
  height: 100%;
  display: block;
  margin: auto;
  border-radius: 12px;
  border: 1px solid var(--separatorColor);
}

.CoreIFrame .mask {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0);
  border-radius: 12px;
}

.CoreIFrame.selected .mask {
  display: none;
}
</style>
