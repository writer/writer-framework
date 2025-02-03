<template>
	<div v-if="ssbm.isSingleSelectionActive" class="BuilderSettingsVisibility">
		<BuilderSectionTitle icon="visibility" label="Visibility" />
		<div class="main">
			<WdsTabs v-model="tab" :tabs="tabs" />
			<WdsFieldWrapper
				v-if="
					typeof component.visible != 'undefined' &&
					component.visible.expression === 'custom'
				"
				:hint="hint"
			>
				<BuilderTemplateInput
					:value="component.visible.binding"
					type="state"
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
			</WdsFieldWrapper>
		</div>
	</div>
</template>

<script setup lang="ts">
import { computed, inject } from "vue";
import { useComponentActions } from "../useComponentActions";
import injectionKeys from "@/injectionKeys";
import BuilderTemplateInput from "./BuilderTemplateInput.vue";
import WdsFieldWrapper from "@/wds/WdsFieldWrapper.vue";
import BuilderSectionTitle from "./BuilderSectionTitle.vue";
import WdsTabs, { WdsTabOptions } from "@/wds/WdsTabs.vue";

type Mode = "yes" | "no" | "custom";

const tabs: WdsTabOptions<Mode>[] = [
	{ label: "Yes", value: "yes" },
	{ label: "No", value: "no" },
	{ label: "Custom", value: "custom" },
];

const tab = computed<Mode>({
	get() {
		const visible = component.value.visible;
		if (visible?.expression === "custom") return "custom";

		return visible === undefined || visible.expression === true
			? "yes"
			: "no";
	},
	set(value: Mode) {
		if (value === "custom") {
			setVisibleValue(
				component.value.id,
				"custom",
				component.value.visible?.binding,
				component.value.visible?.reversed,
			);
		} else {
			setVisibleValue(component.value.id, value === "yes");
		}
	},
});

const wf = inject(injectionKeys.core);
const ssbm = inject(injectionKeys.builderManager);
const { setVisibleValue } = useComponentActions(wf, ssbm);

const component = computed(() =>
	wf.getComponentById(ssbm.firstSelectedId.value),
);

const hint =
	'Reference a state or context element that will evaluate to true or false. Reference the element directly, i.e. use "my_var" instead of "@{my_var}".';
</script>

<style scoped>
@import "../sharedStyles.css";

.main {
	margin-top: 16px;
	display: flex;
	flex-direction: column;
	gap: 4px;
}

.flexRow {
	margin-top: 4px;
	display: flex;
	flex-direction: row;
	gap: 8px;
}
</style>
