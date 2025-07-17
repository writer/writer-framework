<script setup lang="ts">
import injectionKeys from "@/injectionKeys";
import WdsLoaderDots from "@/wds/WdsLoaderDots.vue";
import WdsIcon from "@/wds/WdsIcon.vue";
import { WdsColor } from "@/wds/tokens";
import { computed, inject } from "vue";

const props = defineProps({
	blueprintId: { type: String, required: true },
});

const core = inject(injectionKeys.core);
const wfbm = inject(injectionKeys.builderManager);

const blueprintBlocks = computed(() => core.getComponents(props.blueprintId));
const blueprintBlocksId = computed(() =>
	blueprintBlocks.value.map((b) => b.id),
);

const result = computed(() => {
	const logs = wfbm.getLogEntries().filter((l) => {
		if (!l.blueprintExecution) return false;

		const isRelated = l.blueprintExecution.summary.some((v) =>
			blueprintBlocksId.value.includes(v.componentId),
		);
		return isRelated;
	});

	const message = logs.at(0)?.blueprintExecution.summary.at(-1);
	if (!message) return undefined;

	if (message.outcome === "in_progress") return "in_progress";

	const component = core.getComponentById(message.componentId);
	const def = core.getComponentDefinition(component.type);

	return def.outs?.[message.outcome]?.style ?? "success";
});
</script>

<template>
	<div class="BuilderBlueprintState">
		<slot v-if="!result" name="unknown"></slot>
		<slot v-else-if="result === 'success'" name="success">
			<div
				class="BuilderBlueprintState__status BuilderBlueprintState__status--success"
			>
				<WdsIcon name="check" />
			</div>
		</slot>
		<slot v-else-if="result === 'error'" name="error">
			<div
				class="BuilderBlueprintState__status BuilderBlueprintState__status--error"
			>
				<WdsIcon name="circle-alert" />
			</div>
		</slot>
		<slot v-else-if="result === 'in_progress'" name="running">
			<WdsLoaderDots
				class="BuilderBlueprintState__status"
				:color="WdsColor.Gray5"
			/>
		</slot>
	</div>
</template>

<style scoped>
.BuilderBlueprintState__status {
	height: 18px;
	width: 18px;
	border-radius: 50%;

	display: flex;
	align-items: center;
	justify-content: center;
}
.BuilderBlueprintState__status--success {
	background-color: var(--wdsColorGreen3);
}
.BuilderBlueprintState__status--error {
	background-color: var(--wdsColorOrange5);
}
</style>
