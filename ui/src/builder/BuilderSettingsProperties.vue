<template>
	<div
		class="BuilderSettingsProperties"
		v-if="ssbm.isSelectionActive() && fields"
	>
		<div class="sectionTitle">
			<i class="ri-equalizer-line ri-xl"></i>
			<h3>Properties</h3>
		</div>
		<div>
			<div
				v-for="propertyCategory in fieldCategories"
				class="propertyCategory"
				:key="propertyCategory"
			>
				<div
					class="title"
					v-if="fieldsByCategory[propertyCategory].length > 0"
				>
					<h4>{{ propertyCategory }}</h4>
				</div>
				<div
					v-for="[fieldKey, fieldValue] in fieldsByCategory[
						propertyCategory
					]"
					:key="fieldKey"
				>
					<div class="fieldWrapper">
						<div class="name">
							{{ fieldValue.name ?? fieldKey
							}}<span class="type"> : {{ fieldValue.type }}</span>
						</div>
						<BuilderFieldsColor
							class="content"
							:field-key="fieldKey"
							:component-id="selectedComponent.id"
							v-if="fieldValue.type == FieldType.Color"
						></BuilderFieldsColor>

						<BuilderFieldsShadow
							class="content"
							:field-key="fieldKey"
							:component-id="selectedComponent.id"
							v-if="fieldValue.type == FieldType.Shadow"
						></BuilderFieldsShadow>

						<BuilderFieldsKeyValue
							class="content"
							:field-key="fieldKey"
							:component-id="selectedComponent.id"
							v-if="fieldValue.type == FieldType.KeyValue"
						></BuilderFieldsKeyValue>

						<BuilderFieldsText
							:field-key="fieldKey"
							:component-id="selectedComponent.id"
							v-if="fieldValue.type == FieldType.Text"
						></BuilderFieldsText>

						<BuilderFieldsText
							:field-key="fieldKey"
							:component-id="selectedComponent.id"
							v-if="fieldValue.type == FieldType.Number"
						></BuilderFieldsText>

						<BuilderFieldsText
							:field-key="fieldKey"
							:component-id="selectedComponent.id"
							v-if="fieldValue.type == FieldType.IdKey"
						></BuilderFieldsText>

						<BuilderFieldsObject
							class="content"
							:field-key="fieldKey"
							:component-id="selectedComponent.id"
							v-if="fieldValue.type == FieldType.Object"
						></BuilderFieldsObject>

						<BuilderFieldsWidth
							class="content"
							:field-key="fieldKey"
							:component-id="selectedComponent.id"
							v-if="fieldValue.type == FieldType.Width"
						></BuilderFieldsWidth>

						<BuilderFieldsAlign
							class="content"
							direction="horizontal"
							:field-key="fieldKey"
							:component-id="selectedComponent.id"
							v-if="fieldValue.type == FieldType.HAlign"
						></BuilderFieldsAlign>

						<BuilderFieldsAlign
							class="content"
							direction="vertical"
							:field-key="fieldKey"
							:component-id="selectedComponent.id"
							v-if="fieldValue.type == FieldType.VAlign"
						></BuilderFieldsAlign>

						<BuilderFieldsPadding
							class="content"
							:field-key="fieldKey"
							:component-id="selectedComponent.id"
							v-if="fieldValue.type == FieldType.Padding"
						></BuilderFieldsPadding>

						<div class="desc" v-if="fieldValue.desc">
							{{ fieldValue.desc }}
						</div>
					</div>
				</div>
			</div>
		</div>
	</div>
</template>

<script setup lang="ts">
import { computed, inject } from "vue";
import BuilderFieldsKeyValue from "./BuilderFieldsKeyValue.vue";
import { FieldType, FieldCategory } from "../streamsyncTypes";
import BuilderFieldsColor from "./BuilderFieldsColor.vue";
import BuilderFieldsShadow from "./BuilderFieldsShadow.vue";
import BuilderFieldsText from "./BuilderFieldsText.vue";
import BuilderFieldsObject from "./BuilderFieldsObject.vue";
import BuilderFieldsWidth from "./BuilderFieldsWidth.vue";
import BuilderFieldsAlign from "./BuilderFieldsAlign.vue";
import BuilderFieldsPadding from "./BuilderFieldsPadding.vue";
import injectionKeys from "../injectionKeys";

const ss = inject(injectionKeys.core);
const ssbm = inject(injectionKeys.builderManager);

const selectedComponent = computed(() => {
	return ss.getComponentById(ssbm.getSelectedId());
});

const fields = computed(() => {
	const { type } = selectedComponent.value;
	const definition = ss.getComponentDefinition(type);
	return definition.fields;
});

const fieldCategories = [FieldCategory.General, FieldCategory.Style];

const fieldsByCategory = computed(() => {
	const entries = Object.entries(fields.value);
	const result = {
		[FieldCategory.General]: entries.filter(
			([_, fieldValue]) =>
				!fieldValue.category ||
				fieldValue.category == FieldCategory.General
		),
		[FieldCategory.Style]: entries.filter(
			([_, fieldValue]) => fieldValue.category == FieldCategory.Style
		),
	};
	return result;
});
</script>

<style scoped>
@import "./sharedStyles.css";

.BuilderSettingsProperties {
	padding: 24px;
}

.propertyCategory .title {
	margin-top: 24px;
}

textarea.content {
	resize: vertical;
	height: 8em;
}

input[type="color"].content {
	height: 48px;
}
</style>
