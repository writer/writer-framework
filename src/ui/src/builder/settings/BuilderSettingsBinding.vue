<template>
	<div
		v-if="ssbm.isSingleSelectionActive"
		:inert="isReadOnly"
		class="BuilderSettingsBinding"
	>
		<WdsTitle2>Binding</WdsTitle2>
		<WdsFieldWrapper
			class="BuilderSettingsBinding__main"
			label="Link Variable"
			:hint="hint"
		>
			<BuilderTemplateInput
				type="state"
				:value="component.binding?.stateRef"
				:component-id="ssbm.firstSelectedId.value"
				@input="
					(ev: Event) =>
						setBinding(
							component.id,
							(ev.target as HTMLInputElement).value,
						)
				"
			/>
		</WdsFieldWrapper>
	</div>
</template>

<script setup lang="ts">
import { computed, inject } from "vue";
import { useComponentActions } from "../useComponentActions";
import injectionKeys from "@/injectionKeys";
import BuilderTemplateInput from "./BuilderTemplateInput.vue";
import WdsFieldWrapper from "@/wds/WdsFieldWrapper.vue";
import WdsTitle2 from "@/wds/WdsTitle2.vue";

defineProps({
	isReadOnly: { type: Boolean, required: true },
});

const hint =
	"Connect the result of this block to a dynamic variable you can use across this agent";

const wf = inject(injectionKeys.core)!;
const ssbm = inject(injectionKeys.builderManager)!;
const { setBinding } = useComponentActions(wf, ssbm);

const component = computed(() =>
	wf.getComponentById(ssbm.firstSelectedId.value),
);
</script>

<style scoped>
@import "../sharedStyles.css";

.BuilderSettingsBinding {
	padding: 24px;
}

.BuilderSettingsBinding[inert] {
	opacity: 0.7;
}

.BuilderSettingsBinding__main {
	margin-top: 16px;
}
</style>
