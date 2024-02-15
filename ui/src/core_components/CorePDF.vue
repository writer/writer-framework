<template>
	<div class="CorePDF">
		<object class="pdf" :data="fields.source.value" type="application/pdf" width="100%" height="100%">
			<p>
				You don't have a PDF plugin, but you can
				<a :href="fields.source.value">download the PDF file. </a>
			</p>
		</object>
		<div class="mask" />
	</div>
</template>

<script lang='ts'>
import { FieldType } from "../streamsyncTypes";
import { cssClasses } from "../renderer/sharedStyleFields";

const description =
	"A component to embed a PDF document.";

export default {
	streamsync: {
		name: "PDF",
		description,
		category: "Embed",
		fields: {
			source: {
				name: "Pdf source",
				type: FieldType.Text,
				desc: "Either URL or Base64",
			},
			cssClasses,
		},
	},
};
</script>

<script setup lang="ts">
import { inject } from "vue";
import injectionKeys from "../injectionKeys";
const fields = inject(injectionKeys.evaluatedFields);
</script>

<style scoped>
@import "../renderer/sharedStyles.css";
.CorePDF {
  position: relative;
  width: 100%;
  height: 80vh;
}

.CorePDF .pdf {
  width: 100%;
  height: 100%;
  display: block;
  margin: auto;
  border: 1px solid var(--separatorColor);
}

.CorePDF .mask {
  pointer-events: none;
}

.CorePDF.beingEdited .mask {
  pointer-events: all;
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0);
}

.CorePDF.beingEdited.selected .mask {
  pointer-events: none;
}
</style>

