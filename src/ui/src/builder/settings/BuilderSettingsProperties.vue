<template>
	<div
		v-if="ssbm.isSelectionActive() && fields"
		class="BuilderSettingsProperties"
	>
		<div
			v-for="propertyCategory in fieldCategories"
			:key="propertyCategory"
			class="BuilderSettingsProperties__category"
		>
			<h4
				v-if="fieldsByCategory[propertyCategory].length > 0"
				class="BuilderSettingsProperties__category__title"
			>
				{{ propertyCategory }}
			</h4>
			<div
				v-for="[fieldKey, fieldValue] in fieldsByCategory[
					propertyCategory
				]"
				:key="fieldKey"
				class="BuilderSettingsProperties__category__field"
			>
				<WdsFieldWrapper
					:label="
						propertyCategory === 'Tools'
							? undefined
							: fieldValue.name ?? fieldKey
					"
					:hint="fieldValue.desc"
					:unit="fieldValue.type"
				>
					<BuilderFieldsColor
						v-if="fieldValue.type == FieldType.Color"
						:field-key="fieldKey"
						:component-id="selectedComponent.id"
					></BuilderFieldsColor>

					<BuilderFieldsShadow
						v-if="fieldValue.type == FieldType.Shadow"
						:field-key="fieldKey"
						:component-id="selectedComponent.id"
					></BuilderFieldsShadow>

					<BuilderFieldsKeyValue
						v-if="fieldValue.type == FieldType.KeyValue"
						:field-key="fieldKey"
						:component-id="selectedComponent.id"
						:instance-path="selectedInstancePath"
					></BuilderFieldsKeyValue>

					<BuilderFieldsText
						v-if="fieldValue.type == FieldType.Text"
						:field-key="fieldKey"
						:component-id="selectedComponent.id"
					></BuilderFieldsText>

					<BuilderFieldsText
						v-if="fieldValue.type == FieldType.Number"
						:field-key="fieldKey"
						:component-id="selectedComponent.id"
					></BuilderFieldsText>

					<BuilderFieldsText
						v-if="fieldValue.type == FieldType.IdKey"
						:field-key="fieldKey"
						:component-id="selectedComponent.id"
					></BuilderFieldsText>

					<BuilderFieldsObject
						v-if="fieldValue.type == FieldType.Object"
						:field-key="fieldKey"
						:component-id="selectedComponent.id"
					></BuilderFieldsObject>

					<BuilderFieldsWidth
						v-if="fieldValue.type == FieldType.Width"
						:field-key="fieldKey"
						:component-id="selectedComponent.id"
					></BuilderFieldsWidth>

					<BuilderFieldsAlign
						v-if="fieldValue.type == FieldType.HAlign"
						direction="horizontal"
						:field-key="fieldKey"
						:component-id="selectedComponent.id"
					></BuilderFieldsAlign>

					<BuilderFieldsAlign
						v-if="fieldValue.type == FieldType.VAlign"
						direction="vertical"
						:field-key="fieldKey"
						:component-id="selectedComponent.id"
					></BuilderFieldsAlign>

					<BuilderFieldsPadding
						v-if="fieldValue.type == FieldType.Padding"
						:field-key="fieldKey"
						:component-id="selectedComponent.id"
					></BuilderFieldsPadding>

					<BuilderFieldsTools
						v-if="fieldValue.type == FieldType.Tools"
						:field-key="fieldKey"
						:component-id="selectedComponent.id"
					>
					</BuilderFieldsTools>
				</WdsFieldWrapper>
			</div>
		</div>
	</div>
</template>

<script setup lang="ts">
import { computed, inject } from "vue";
import injectionKeys from "../../injectionKeys";
import { parseInstancePathString } from "@/renderer/instancePath";
import { FieldCategory, FieldType, InstancePath } from "@/writerTypes";
import BuilderFieldsAlign from "./BuilderFieldsAlign.vue";
import BuilderFieldsColor from "./BuilderFieldsColor.vue";
import BuilderFieldsKeyValue from "./BuilderFieldsKeyValue.vue";
import BuilderFieldsObject from "./BuilderFieldsObject.vue";
import BuilderFieldsPadding from "./BuilderFieldsPadding.vue";
import BuilderFieldsShadow from "./BuilderFieldsShadow.vue";
import BuilderFieldsText from "./BuilderFieldsText.vue";
import BuilderFieldsWidth from "./BuilderFieldsWidth.vue";
import BuilderFieldsTools from "./BuilderFieldsTools.vue";
import WdsFieldWrapper from "@/wds/WdsFieldWrapper.vue";

const wf = inject(injectionKeys.core);
const ssbm = inject(injectionKeys.builderManager);

const selectedInstancePath = computed<InstancePath>(() =>
	parseInstancePathString(ssbm.getSelection()?.instancePath),
);

const selectedComponent = computed(() => {
	return wf.getComponentById(ssbm.getSelectedId());
});

const fields = computed(() => {
	const { type } = selectedComponent.value;
	const definition = wf.getComponentDefinition(type);
	return definition.fields;
});

const fieldCategories = computed(() => {
	return [
		FieldCategory.General,
		FieldCategory.Style,
		FieldCategory.Tools,
	].filter((c) => fieldsByCategory.value[c]?.length);
});

const fieldsByCategory = computed(() => {
	const entries = Object.entries(fields.value);
	const result = {
		[FieldCategory.General]: entries.filter(
			([_, fieldValue]) =>
				!fieldValue.category ||
				fieldValue.category == FieldCategory.General,
		),
		[FieldCategory.Style]: entries.filter(
			([_, fieldValue]) => fieldValue.category == FieldCategory.Style,
		),
		[FieldCategory.Tools]: entries.filter(
			([_, fieldValue]) => fieldValue.category == FieldCategory.Tools,
		),
	};
	return result;
});
</script>

<style scoped>
@import "../sharedStyles.css";

.BuilderSettingsProperties {
	padding: 24px;

	display: flex;
	flex-direction: column;
	gap: 16px;
}

.BuilderSettingsProperties__category {
	display: flex;
	flex-direction: column;
	gap: 16px;
}

.BuilderSettingsProperties__category__title {
	color: var(--builderSecondaryTextColor);
	font-weight: 500;
	font-size: 12px;
}
</style>
