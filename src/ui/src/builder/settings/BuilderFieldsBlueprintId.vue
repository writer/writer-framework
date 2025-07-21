<template>
	<div class="BuilderFieldsBlueprintId" :data-automation-key="props.fieldKey">
		<WdsTextInput :model-value="blueprintId" disabled />
	</div>
</template>

<script setup lang="ts">
import { inject, computed } from "vue";
import injectionKeys from "@/injectionKeys";
import WdsTextInput from "@/wds/WdsTextInput.vue";

const wf = inject(injectionKeys.core);

const props = defineProps({
	componentId: { type: String, required: true },
	fieldKey: { type: String, required: true },
});

const component = computed(() => wf.getComponentById(props.componentId));
const blueprintId = computed(() => component.value?.parentId ?? "");
</script>

<style scoped>
.BuilderFieldsBlueprintId {
	display: flex;
}
</style>
