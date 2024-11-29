<template>
	<div v-if="ssbm.isSelectionActive()" class="BuilderSettingsBinding">
		<div class="sectionTitle">
			<i class="material-symbols-outlined">link</i>
			<h3>Binding</h3>
		</div>
		<div class="main">
			<div class="fieldWrapper">
				<span class="name">State element</span>
				<BuilderTemplateInput
					type="state"
					class="content"
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
				<div class="desc">
					Links this component to a state element, in a two-way
					fashion. Reference the state element directly, i.e. use
					"my_var" instead of "@{my_var}".
				</div>
			</div>
		</div>
	</div>
</template>

<script setup lang="ts">
import { computed, inject } from "vue";
import { useComponentActions } from "../useComponentActions";
import injectionKeys from "../../injectionKeys";
import BuilderTemplateInput from "./BuilderTemplateInput.vue";

const wf = inject(injectionKeys.core);
const ssbm = inject(injectionKeys.builderManager);
const { setBinding } = useComponentActions(wf, ssbm);

const component = computed(() => wf.getComponentById(ssbm.getSelectedId()));
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
