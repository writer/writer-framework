<template>
	<div v-if="ssbm.isSingleSelectionActive" class="BuilderSettingsBinding">
		<BuilderSectionTitle icon="link" label="Binding" />
		<div class="main">
			<WdsFieldWrapper label="State element" :hint="hint">
				<BuilderTemplateInput
					type="state"
					:value="component.binding?.stateRef"
					placeholder="my_var"
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
	</div>
</template>

<script setup lang="ts">
import { computed, inject } from "vue";
import { useComponentActions } from "../useComponentActions";
import injectionKeys from "../../injectionKeys";
import BuilderTemplateInput from "./BuilderTemplateInput.vue";
import WdsFieldWrapper from "@/wds/WdsFieldWrapper.vue";

const hint =
	'Links this component to a state element, in a two-way fashion. Reference the state element directly, i.e. use "my_var" instead of "@{my_var}".';

const wf = inject(injectionKeys.core);
const ssbm = inject(injectionKeys.builderManager);
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

.main {
	margin-top: 16px;
}

.content {
	padding: 16px 12px 12px 12px;
	width: 100%;
}
</style>
