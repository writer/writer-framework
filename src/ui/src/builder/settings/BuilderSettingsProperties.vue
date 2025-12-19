<template>
	<div v-if="ssbm.isSingleSelectionActive" class="BuilderSettingsProperties">
		<WdsTabs
			v-if="fieldCategories.length > 1"
			v-model="selectedCategoryTab"
			variant="bar"
			:tabs="fieldCategoryTabOptions"
		/>

		<div
			v-for="propertyCategory in fieldCategories.length > 1
				? [selectedCategoryTab]
				: fieldCategories"
			:key="propertyCategory"
			:inert="isReadOnly"
			class="BuilderSettingsProperties__category"
		>
			<div
				v-for="[fieldKey, fieldValue] in fieldsByCategory[
					propertyCategory
				]"
				:key="fieldKey"
				class="BuilderSettingsProperties__category__field"
			>
				<BuilderFieldsCheckbox
					v-if="fieldValue.type === FieldType.Boolean"
					:field-key="fieldKey"
					:component-id="selectedComponent.id"
					:label="fieldValue.name ?? fieldKey"
					:hint="fieldValue.desc"
					:unit="fieldValue.type"
					:error="errorsByFields[fieldKey]"
				/>

				<BuilderFieldsWriterResourceId
					v-else-if="fieldValue.type === FieldType.WriterGraphId"
					is-binding-button-shown
					:field-key="fieldKey"
					:component-id="selectedComponent.id"
					:label="fieldValue.name ?? fieldKey"
					:hint="fieldValue.desc"
					:unit="fieldValue.type"
					:error="errorsByFields[fieldKey]"
					resource-type="graph"
				/>

				<BuilderFieldsWriterResourceId
					v-else-if="fieldValue.type === FieldType.WriterGraphIds"
					is-binding-button-shown
					:field-key="fieldKey"
					:component-id="selectedComponent.id"
					:label="fieldValue.name ?? fieldKey"
					:hint="fieldValue.desc"
					:unit="fieldValue.type"
					:error="errorsByFields[fieldKey]"
					resource-type="graph"
					enable-multi-selection
				/>

				<BuilderFieldsWriterResourceId
					v-else-if="fieldValue.type === FieldType.WriterAppId"
					:field-key="fieldKey"
					:component-id="selectedComponent.id"
					:label="fieldValue.name ?? fieldKey"
					:hint="fieldValue.desc"
					:unit="fieldValue.type"
					:error="errorsByFields[fieldKey]"
					resource-type="application"
				/>

				<BuilderFieldsWriterResourceId
					v-else-if="fieldValue.type === FieldType.WriterModelId"
					:field-key="fieldKey"
					:component-id="selectedComponent.id"
					:label="fieldValue.name ?? fieldKey"
					:hint="fieldValue.desc"
					:unit="fieldValue.type"
					:error="errorsByFields[fieldKey]"
					resource-type="model"
				/>

				<WdsFieldWrapper
					v-else
					:label="
						propertyCategory === 'Tools'
							? undefined
							: fieldValue.name ?? fieldKey
					"
					:hint="fieldValue.desc"
					:unit="fieldValue.type"
					:error="errorsByFields[fieldKey]"
					:is-expansible="isExpansible(fieldValue)"
					:should-expand="isExpansible(fieldValue) && isFieldExpanded"
					@expand="handleExpand(fieldKey)"
					@shrink="handleShrink(fieldKey)"
				>
					<BuilderFieldsColor
						v-if="fieldValue.type == FieldType.Color"
						:field-key="fieldKey"
						:component-id="selectedComponent.id"
						:error="errorsByFields[fieldKey]"
					/>

					<BuilderFieldsShadow
						v-if="fieldValue.type == FieldType.Shadow"
						:field-key="fieldKey"
						:component-id="selectedComponent.id"
						:error="errorsByFields[fieldKey]"
					/>

					<BuilderFieldsKeyValue
						v-if="fieldValue.type == FieldType.KeyValue"
						:field-key="fieldKey"
						:component-id="selectedComponent.id"
						:instance-path="selectedInstancePath"
						:error="errorsByFields[fieldKey]"
					/>

					<BuilderFieldsText
						v-if="
							fieldValue.type == FieldType.Text ||
							fieldValue.type == FieldType.Number ||
							fieldValue.type == FieldType.Binding ||
							fieldValue.type == FieldType.IdKey
						"
						:type="
							fieldValue.type == FieldType.Binding
								? 'state'
								: 'template'
						"
						:field-key="fieldKey"
						:field-control="fieldValue.control"
						:component-id="selectedComponent.id"
						:default-value="fieldValue.default"
						:error="errorsByFields[fieldKey]"
					/>

					<BuilderFieldsBlueprintId
						v-if="fieldValue.type == FieldType.BlueprintId"
						:field-key="fieldKey"
						:component-id="selectedComponent.id"
					/>

					<BuilderFieldsBlueprintKey
						v-if="fieldValue.type == FieldType.BlueprintKey"
						:field-key="fieldKey"
						:component-id="selectedComponent.id"
					/>

					<BuilderFieldsHandler
						v-if="fieldValue.type == FieldType.Handler"
						:field-key="fieldKey"
						:component-id="selectedComponent.id"
					/>

					<BuilderFieldsObject
						v-if="fieldValue.type == FieldType.Object"
						:field-key="fieldKey"
						:component-id="selectedComponent.id"
						:default-value="fieldValue.default"
						:error="errorsByFields[fieldKey]"
					/>

					<BuilderFieldsCode
						v-if="fieldValue.type == FieldType.JSONInput"
						:field-key="fieldKey"
						:component-id="selectedComponent.id"
						:is-expanded="expandedFields.has(fieldKey)"
						:input-language="'json'"
					/>

					<BuilderFieldsWidth
						v-if="fieldValue.type == FieldType.Width"
						:field-key="fieldKey"
						:component-id="selectedComponent.id"
						:error="errorsByFields[fieldKey]"
					/>

					<BuilderFieldsAlign
						v-if="fieldValue.type == FieldType.HAlign"
						direction="horizontal"
						:field-key="fieldKey"
						:component-id="selectedComponent.id"
						:error="errorsByFields[fieldKey]"
					/>

					<BuilderFieldsAlign
						v-if="fieldValue.type == FieldType.VAlign"
						direction="vertical"
						:field-key="fieldKey"
						:component-id="selectedComponent.id"
						:error="errorsByFields[fieldKey]"
					/>

					<BuilderFieldsPadding
						v-if="fieldValue.type == FieldType.Padding"
						:field-key="fieldKey"
						:component-id="selectedComponent.id"
						:error="errorsByFields[fieldKey]"
					/>

					<BuilderFieldsToolsWithMcp
						v-if="
							fieldValue.type == FieldType.Tools &&
							selectedComponent.type ===
								'blueprints_writerchatreplywithtoolconfig'
						"
						:field-key="fieldKey"
						:component-id="selectedComponent.id"
					/>
					<BuilderFieldsTools
						v-else-if="fieldValue.type == FieldType.Tools"
						:field-key="fieldKey"
						:component-id="selectedComponent.id"
					/>

					<BuilderFieldsCode
						v-if="
							fieldValue.type == FieldType.Code ||
							fieldValue.type == FieldType.Eval
						"
						:field-key="fieldKey"
						:component-id="selectedComponent.id"
						:is-expanded="expandedFields.has(fieldKey)"
						:input-language="'python'"
						:single-line="fieldValue.type == FieldType.Eval"
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
import BuilderFieldsCheckbox from "./BuilderFieldsCheckbox.vue";
import BuilderFieldsKeyValue from "./BuilderFieldsKeyValue.vue";
import BuilderFieldsObject from "./BuilderFieldsObject.vue";
import BuilderFieldsPadding from "./BuilderFieldsPadding.vue";
import BuilderFieldsShadow from "./BuilderFieldsShadow.vue";
import BuilderFieldsText from "./BuilderFieldsText.vue";
import BuilderFieldsWidth from "./BuilderFieldsWidth.vue";
import BuilderFieldsTools from "./BuilderFieldsTools.vue";
import BuilderFieldsToolsWithMcp from "./BuilderFieldsToolsWithMcp.vue";
import WdsFieldWrapper from "@/wds/WdsFieldWrapper.vue";
import BuilderFieldsCode from "./BuilderFieldsCode.vue";
import BuilderFieldsBlueprintKey from "./BuilderFieldsBlueprintKey.vue";
import BuilderFieldsBlueprintId from "./BuilderFieldsBlueprintId.vue";
import BuilderFieldsHandler from "./BuilderFieldsHandler.vue";
import BuilderFieldsWriterResourceId from "./BuilderFieldsWriterResourceId.vue";
import BuilderFieldsComponentId from "./BuilderFieldsComponentId.vue";
import BuilderFieldsComponentEventType from "./BuilderFieldsComponentEventType.vue";
import WdsTabs, { type WdsTabOptions } from "@/wds/WdsTabs.vue";
import { useFieldsErrors } from "@/renderer/useFieldsErrors";
import { useEvaluator } from "@/renderer/useEvaluator";

defineProps({
	isReadOnly: { type: Boolean },
});

const wf = inject(injectionKeys.core);
const ssbm = inject(injectionKeys.builderManager);
const secretsManager = inject(injectionKeys.secretsManager);

const expandedFields = ref(new Set());

const isFieldExpanded = computed(() => {
	return (
		ssbm.expandedEditorForComponent.value === selectedComponent.value?.id
	);
});

const selectedInstancePath = computed<InstancePath>(() =>
	parseInstancePathString(ssbm.firstSelectedItem?.value?.instancePath),
);

const selectedComponent = computed(() => {
	return wf.getComponentById(ssbm.firstSelectedId.value);
});

const componentDefinition = computed(() =>
	wf.getComponentDefinition(selectedComponent.value?.type),
);

const { getEvaluatedFields } = useEvaluator(wf, secretsManager);
const evaluatedFields = computed(() =>
	getEvaluatedFields(selectedInstancePath.value),
);

const fields = computed(() => {
	const entries = Object.entries(
		componentDefinition.value?.fields ?? {},
	).filter(([_, v]) => {
		if (v.isArtifactField) return false;
		if (v.enabled === undefined) return true;
		return v.enabled({ evaluatedFields: evaluatedFields.value });
	});

	return Object.fromEntries(entries);
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

const selectedCategoryTab = ref<FieldCategory>(FieldCategory.General);

const LABELS_BY_CATEGORY = Object.freeze<Record<FieldCategory, string>>({
	[FieldCategory.General]: "Configure",
	[FieldCategory.Style]: "Style",
	[FieldCategory.Tools]: "Tools",
});

const fieldCategoryTabOptions = computed<WdsTabOptions<FieldCategory>[]>(() => {
	return fieldCategories.value.map((category) => ({
		label: LABELS_BY_CATEGORY[category] ?? category,
		value: category,
	}));
});

const fieldCategories = computed(() => {
	return [
		FieldCategory.General,
		FieldCategory.Style,
		FieldCategory.Tools,
	].filter((c) => fieldsByCategory.value[c]?.length);
});

type FieldEntry = [string, WriterComponentDefinitionField];

const fieldsByCategory = computed<Record<FieldCategory, FieldEntry[]>>(() => {
	const result: Record<FieldCategory, FieldEntry[]> = {
		[FieldCategory.General]: [],
		[FieldCategory.Style]: [],
		[FieldCategory.Tools]: [],
	};

	Object.entries(fields.value).forEach(([k, v]) => {
		const category = v.category || FieldCategory.General;

		if (result[category]) {
			result[category].push([k, v]);
		}
	});

	return {
		[FieldCategory.General]: sortByOrder(result[FieldCategory.General]),
		[FieldCategory.Style]: sortByOrder(result[FieldCategory.Style]),
		[FieldCategory.Tools]: sortByOrder(result[FieldCategory.Tools]),
	};
});

function sortByOrder(fieldEntries: FieldEntry[]): FieldEntry[] {
	return fieldEntries
		.map((item, itemIndex) => [item, itemIndex] as const)
		.sort(([a, aIndex], [b, bIndex]) => {
			const aOrder = a[1].order ?? 0;
			const bOrder = b[1].order ?? 0;

			return bOrder - aOrder || aIndex - bIndex;
		})
		.map(([item]) => item);
}

function handleExpand(fieldKey: string) {
	ssbm.expandedEditorForComponent.value = selectedComponent.value?.id ?? null;
	expandedFields.value.add(fieldKey);
}

function handleShrink(fieldKey: string) {
	ssbm.expandedEditorForComponent.value = null;
	expandedFields.value.delete(fieldKey);
}
</script>

<style scoped>
@import "../sharedStyles.css";

.BuilderSettingsProperties {
	padding: 24px;

	display: flex;
	flex-direction: column;
	gap: 24px;
}

.BuilderSettingsProperties__category {
	display: flex;
	flex-direction: column;
	gap: 24px;
}

.BuilderSettingsProperties__category[inert] {
	opacity: 0.7;
}
</style>
