<template>
	<div v-if="ssbm.isSelectionActive()" class="BuilderSettingsVisibility">
		<div class="sectionTitle">
			<i class="material-symbols-outlined"> visibility </i>
			<h3>Visibility</h3>
		</div>
		<div class="main">
			<div class="chipStack">
				<div
					class="chip"
					:class="{
						active:
							typeof component.visible == 'undefined' ||
							component.visible.expression === true,
					}"
					@click="() => setVisibleValue(component.id, true)"
				>
					Yes
				</div>
				<div
					class="chip"
					:class="{ active: component.visible?.expression === false }"
					@click="() => setVisibleValue(component.id, false)"
				>
					No
				</div>
				<div
					class="chip"
					:class="{
						active: component.visible?.expression === 'custom',
					}"
					@click="
						() =>
							setVisibleValue(
								component.id,
								'custom',
								component.visible?.binding,
								component.visible?.reversed,
							)
					"
				>
					Custom
				</div>
			</div>
			<div
				v-if="
					typeof component.visible != 'undefined' &&
					component.visible.expression === 'custom'
				"
				class="fieldWrapper"
			>
				<span class="name">Visibility value</span>
				<BuilderTemplateInput
					:value="component.visible.binding"
					type="state"
					class="content"
					placeholder="my_visibility_state_value"
					@input="
						(ev: Event) =>
							setVisibleValue(
								component.id,
								'custom',
								(ev.target as HTMLInputElement).value,
								component.visible.reversed,
							)
					"
				/>
				<div class="flexRow">
					<input
						type="checkbox"
						:checked="component.visible.reversed"
						@input="
							(ev: Event) =>
								setVisibleValue(
									component.id,
									'custom',
									component.visible.binding,
									(ev.target as HTMLInputElement).checked,
								)
						"
					/><span>Reverse</span>
				</div>
				<div class="desc">
					Reference a state or context element that will evaluate to
					true or false. Reference the element directly, i.e. use
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
const { setVisibleValue } = useComponentActions(wf, ssbm);

const component = computed(() => wf.getComponentById(ssbm.getSelectedId()));
</script>

<style scoped>
@import "../sharedStyles.css";

.main {
	margin-top: 16px;
}

.content {
	padding: 16px 12px 12px 12px;
}

.flexRow {
	display: flex;
	flex-direction: row;
	gap: 8px;
}
</style>
