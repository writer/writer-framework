<template>
	<div
		v-if="ssbm.isSingleSelectionActive && fields"
		class="BuilderSettingsProperties"
	>
		<div
			v-for="propertyCategory in fieldCategories"
			:key="propertyCategory"
			class="BuilderSettingsProperties__category"
		>
			<h4
				v-if="
					fieldsByCategory[propertyCategory].length > 0 &&
					propertyCategory !== 'General'
				"
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
					:error="errorsByFields[fieldKey]"
					:is-expansible="isExpansible(fieldValue)"
					@expand="handleExpand(fieldKey)"
					@shrink="handleShrink(fieldKey)"
				>
					<BuilderFieldsColor
						v-if="fieldValue.type == FieldType.Color"
						:field-key="fieldKey"
						:component-id="selectedComponent.id"
						:error="errorsByFields[fieldKey]"
					></BuilderFieldsColor>

					<BuilderFieldsShadow
						v-if="fieldValue.type == FieldType.Shadow"
						:field-key="fieldKey"
						:component-id="selectedComponent.id"
						:error="errorsByFields[fieldKey]"
					></BuilderFieldsShadow>

					<BuilderFieldsKeyValue
						v-if="fieldValue.type == FieldType.KeyValue"
						:field-key="fieldKey"
						:component-id="selectedComponent.id"
						:instance-path="selectedInstancePath"
						:error="errorsByFields[fieldKey]"
					></BuilderFieldsKeyValue>

					<BuilderFieldsText
						v-if="
							fieldValue.type == FieldType.Text ||
							fieldValue.type == FieldType.Boolean
						"
						:field-key="fieldKey"
						:component-id="selectedComponent.id"
						:error="errorsByFields[fieldKey]"
					></BuilderFieldsText>

					<BuilderFieldsBlueprintKey
						v-if="fieldValue.type == FieldType.BlueprintKey"
						:field-key="fieldKey"
						:component-id="selectedComponent.id"
					></BuilderFieldsBlueprintKey>

					<BuilderFieldsHandler
						v-if="fieldValue.type == FieldType.Handler"
						:field-key="fieldKey"
						:component-id="selectedComponent.id"
					></BuilderFieldsHandler>

					<BuilderFieldsText
						v-if="fieldValue.type == FieldType.Number"
						:field-key="fieldKey"
						:component-id="selectedComponent.id"
						:error="errorsByFields[fieldKey]"
					></BuilderFieldsText>

					<BuilderFieldsText
						v-if="fieldValue.type == FieldType.IdKey"
						:field-key="fieldKey"
						:component-id="selectedComponent.id"
						:error="errorsByFields[fieldKey]"
					></BuilderFieldsText>

					<BuilderFieldsObject
						v-if="fieldValue.type == FieldType.Object"
						:field-key="fieldKey"
						:component-id="selectedComponent.id"
						:error="errorsByFields[fieldKey]"
					></BuilderFieldsObject>

					<BuilderFieldsCode
						v-if="fieldValue.type == FieldType.JSONInput"
						:field-key="fieldKey"
						:component-id="selectedComponent.id"
						:is-expanded="expandedFields.has(fieldKey)"
						:input-language="'json'"
					></BuilderFieldsCode>

					<BuilderFieldsWidth
						v-if="fieldValue.type == FieldType.Width"
						:field-key="fieldKey"
						:component-id="selectedComponent.id"
						:error="errorsByFields[fieldKey]"
					></BuilderFieldsWidth>

					<BuilderFieldsAlign
						v-if="fieldValue.type == FieldType.HAlign"
						direction="horizontal"
						:field-key="fieldKey"
						:component-id="selectedComponent.id"
						:error="errorsByFields[fieldKey]"
					></BuilderFieldsAlign>

					<BuilderFieldsAlign
						v-if="fieldValue.type == FieldType.VAlign"
						direction="vertical"
						:field-key="fieldKey"
						:component-id="selectedComponent.id"
						:error="errorsByFields[fieldKey]"
					></BuilderFieldsAlign>

					<BuilderFieldsPadding
						v-if="fieldValue.type == FieldType.Padding"
						:field-key="fieldKey"
						:component-id="selectedComponent.id"
						:error="errorsByFields[fieldKey]"
					></BuilderFieldsPadding>

					<BuilderFieldsTools
						v-if="fieldValue.type == FieldType.Tools"
						:field-key="fieldKey"
						:component-id="selectedComponent.id"
					>
					</BuilderFieldsTools>

					<BuilderFieldsCode
						v-if="fieldValue.type == FieldType.Code"
						:field-key="fieldKey"
						:component-id="selectedComponent.id"
						:is-expanded="expandedFields.has(fieldKey)"
						:input-language="'python'"
					>
					</BuilderFieldsCode>
					<BuilderFieldsWriterResourceId
						v-if="fieldValue.type == FieldType.WriterGraphId"
						:field-key="fieldKey"
						:component-id="selectedComponent.id"
						:error="errorsByFields[fieldKey]"
						resource-type="graph"
					/>
					<BuilderFieldsWriterResourceId
						v-if="fieldValue.type == FieldType.WriterAppId"
						:field-key="fieldKey"
						:component-id="selectedComponent.id"
						:error="errorsByFields[fieldKey]"
						resource-type="application"
					/>
					<BuilderFieldsWriterResourceId
						v-if="fieldValue.type == FieldType.WriterModelId"
						:field-key="fieldKey"
						:component-id="selectedComponent.id"
						:error="errorsByFields[fieldKey]"
						resource-type="model"
					/>
					<BuilderFieldsComponentId
						v-if="fieldValue.type == FieldType.ComponentId"
						:field-key="fieldKey"
						:component-id="selectedComponent.id"
						:error="errorsByFields[fieldKey]"
					/>
					<BuilderFieldsComponentEventType
						v-if="fieldValue.type == FieldType.ComponentEventType"
						:field-key="fieldKey"
						:component-id="selectedComponent.id"
						:error="errorsByFields[fieldKey]"
					/>
				</WdsFieldWrapper>
			</div>
		</div>
	</div>
</template>

<script setup lang="ts">
import { computed, inject, ref } from "vue";
import injectionKeys from "@/injectionKeys";
import { parseInstancePathString } from "@/renderer/instancePath";
import {
	FieldCategory,
	FieldControl,
	FieldType,
	InstancePath,
	WriterComponentDefinitionField,
} from "@/writerTypes";
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
import BuilderFieldsCode from "./BuilderFieldsCode.vue";
import BuilderFieldsBlueprintKey from "./BuilderFieldsBlueprintKey.vue";
import BuilderFieldsHandler from "./BuilderFieldsHandler.vue";
import BuilderFieldsWriterResourceId from "./BuilderFieldsWriterResourceId.vue";
import BuilderFieldsComponentId from "./BuilderFieldsComponentId.vue";
import BuilderFieldsComponentEventType from "./BuilderFieldsComponentEventType.vue";
import { useFieldsErrors } from "@/renderer/useFieldsErrors";

const wf = inject(injectionKeys.core);
const ssbm = inject(injectionKeys.builderManager);
const secretsManager = inject(injectionKeys.secretsManager);

const expandedFields = ref(new Set());

const selectedInstancePath = computed<InstancePath>(() =>
	parseInstancePathString(ssbm.firstSelectedItem?.value?.instancePath),
);

const selectedComponent = computed(() => {
	return wf.getComponentById(ssbm.firstSelectedId.value);
});

const componentDefinition = computed(() => {
	const { type } = selectedComponent.value;
	return wf.getComponentDefinition(type);
});
const fields = computed(() => {
	return componentDefinition.value?.fields;
});

function isExpansible(field: WriterComponentDefinitionField) {
	return (
		field.type === FieldType.Code ||
		field.type === FieldType.JSONInput ||
		field.type === FieldType.Object ||
		field.control === FieldControl.Textarea
	);
}

const errorsByFields = useFieldsErrors(
	wf,
	selectedInstancePath,
	secretsManager,
);

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

function handleExpand(fieldKey: string) {
	expandedFields.value.add(fieldKey);
}

function handleShrink(fieldKey: string) {
	expandedFields.value.delete(fieldKey);
}
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
