<template>
	<div
		v-if="component?.content?.enableValidation === 'yes'"
		class="BuilderSettingsArtifactAPIFieldDefinitions"
	>
		<WdsTitle2>Input field validation</WdsTitle2>
		<p class="BuilderSettingsArtifactAPIFieldDefinitions__description">
			Define the expected structure of JSON payloads sent to this API
			trigger. When enabled, incoming requests will be validated against
			these field definitions.
		</p>

		<div class="BuilderSettingsArtifactAPIFieldDefinitions__controls">
			<WdsButton
				v-if="!isJSONMode"
				variant="special"
				size="small"
				@click="addField"
			>
				<WdsIcon name="plus" />
				Add Field
			</WdsButton>
			<WdsButton
				size="small"
				variant="neutral"
				data-writer-tooltip-placement="left"
				:data-writer-tooltip="
					isJSONMode ? 'Switch to visual editor' : 'Edit as JSON'
				"
				@click="toggleJSONMode"
			>
				<WdsIcon :name="isJSONMode ? 'eye' : 'code'" />
			</WdsButton>
		</div>

		<div
			v-if="fieldDefinitions.length === 0 && !isJSONMode"
			class="BuilderSettingsArtifactAPIFieldDefinitions__empty"
		>
			<WdsIcon name="database" />
			<p>No input fields defined yet.</p>
			<p>
				Add fields to specify what data your API endpoint expects to
				receive.
			</p>
		</div>

		<div
			v-else-if="fieldDefinitions.length > 0 && !isJSONMode"
			class="BuilderSettingsArtifactAPIFieldDefinitions__fields"
		>
			<div
				v-for="(field, index) in fieldDefinitions"
				:key="index"
				class="BuilderSettingsArtifactAPIFieldDefinitions__field"
			>
				<div
					class="BuilderSettingsArtifactAPIFieldDefinitions__field__header"
				>
					<WdsTextInput
						v-model="field.name"
						placeholder="Field name"
						class="BuilderSettingsArtifactAPIFieldDefinitions__field__name"
						@input="updateFieldDefinitions"
					/>
					<WdsButton
						variant="tertiary"
						size="smallIcon"
						@click="removeField(index)"
					>
						<WdsIcon name="trash" />
					</WdsButton>
				</div>

				<div
					class="BuilderSettingsArtifactAPIFieldDefinitions__field__config"
				>
					<WdsDropdownInput
						v-model="field.type"
						class="BuilderSettingsArtifactAPIFieldDefinitions__field__type"
						@change="updateFieldDefinitions"
					>
						<option value="string">String</option>
						<option value="number">Number</option>
						<option value="integer">Integer</option>
						<option value="boolean">Boolean</option>
						<option value="array">Array</option>
						<option value="object">Object</option>
						<option value="null">Null</option>
					</WdsDropdownInput>

					<WdsCheckbox
						v-model="field.required"
						label="Required"
						class="BuilderSettingsArtifactAPIFieldDefinitions__field__required"
						@change="updateFieldDefinitions"
					/>
				</div>
			</div>
		</div>

		<!-- JSON Edit Mode -->
		<WdsFieldWrapper
			v-else-if="isJSONMode"
			label="JSON Field Definitions"
			:is-expansible="true"
			@expand="isExpanded = true"
			@shrink="isExpanded = false"
		>
			<div
				class="BuilderSettingsArtifactAPIFieldDefinitions__json-editor"
			>
				<BuilderEmbeddedCodeEditor
					v-model="jsonValue"
					language="json"
					:variant="isExpanded ? 'half-screen' : 'minimal'"
				/>
			</div>
		</WdsFieldWrapper>

		<!-- Strict validation option -->
		<div class="BuilderSettingsArtifactAPIFieldDefinitions__strict-option">
			<WdsCheckbox
				v-model="strictValidationValue"
				:label="strictValidationField?.name ?? 'Reject unknown fields'"
				:detail="
					strictValidationField?.desc ??
					'Reject payloads that contain fields not defined in the schema'
				"
			/>
		</div>
	</div>
</template>

<script setup lang="ts">
import { computed, inject, ref, watch } from "vue";
import injectionKeys from "@/injectionKeys";
import WdsButton from "@/wds/WdsButton.vue";
import WdsIcon from "@/wds/WdsIcon.vue";
import WdsTitle2 from "@/wds/WdsTitle2.vue";
import WdsTextInput from "@/wds/WdsTextInput.vue";
import WdsDropdownInput from "@/wds/WdsDropdownInput.vue";
import WdsCheckbox from "@/wds/WdsCheckbox.vue";
import BuilderEmbeddedCodeEditor from "../BuilderEmbeddedCodeEditor.vue";
import WdsFieldWrapper from "@/wds/WdsFieldWrapper.vue";
import { useComponentActions } from "../useComponentActions";

interface FieldDefinition {
	name: string;
	type: string;
	required: boolean;
}

const wf = inject(injectionKeys.core);
const ssbm = inject(injectionKeys.builderManager);
const { setContentValue } = useComponentActions(wf, ssbm);

const component = computed(() =>
	wf.getComponentById(ssbm.firstSelectedId.value),
);

const componentDefinition = computed(() => {
	if (!component.value) return null;
	return wf.getComponentDefinition(component.value.type);
});

const strictValidationField = computed(() => {
	return componentDefinition.value?.fields?.strictValidation;
});

// Parse existing field definitions
const fieldDefinitions = ref<FieldDefinition[]>([]);
const isJSONMode = ref(false);
const jsonValue = ref("");
const isExpanded = ref(false);
const strictValidationValue = ref(false);

// Initialize from component content
watch(
	() => component.value?.content?.inputFields,
	(inputFields) => {
		if (inputFields) {
			try {
				const parsed =
					typeof inputFields === "string"
						? JSON.parse(inputFields)
						: inputFields;

				if (Array.isArray(parsed)) {
					fieldDefinitions.value = parsed;
				} else {
					fieldDefinitions.value = [];
				}
			} catch (_e) {
				fieldDefinitions.value = [];
			}
		}
	},
	{ immediate: true },
);

// Initialize strictValidation value
watch(
	() => component.value?.content?.strictValidation,
	(strictValidation) => {
		strictValidationValue.value = strictValidation === "yes";
	},
	{ immediate: true },
);

// Watch for changes to strictValidationValue and update the component
watch(strictValidationValue, () => {
	updateStrictValidation();
});

// Sync jsonValue when fieldDefinitions change
watch(
	fieldDefinitions,
	() => {
		if (!isJSONMode.value) {
			jsonValue.value = JSON.stringify(fieldDefinitions.value, null, 2);
		}
	},
	{ deep: true },
);

function addField() {
	fieldDefinitions.value.push({
		name: "",
		type: "string",
		required: false,
	});
	updateFieldDefinitions();
}

function removeField(index: number) {
	fieldDefinitions.value.splice(index, 1);
	updateFieldDefinitions();
}

function updateFieldDefinitions() {
	if (!component.value) return;

	// Simple field definitions with just name, type, and required
	const cleanFields = fieldDefinitions.value.map((field) => ({
		name: field.name,
		type: field.type,
		required: field.required,
	}));

	const jsonString = JSON.stringify(cleanFields, null, 2);
	jsonValue.value = jsonString;

	setContentValue(component.value.id, "inputFields", jsonString);
}

function updateStrictValidation() {
	if (!component.value) return;

	const newValue = strictValidationValue.value ? "yes" : "no";
	setContentValue(component.value.id, "strictValidation", newValue);
}

function toggleJSONMode() {
	if (isJSONMode.value) {
		// Switching from JSON to visual mode
		try {
			const parsed = JSON.parse(jsonValue.value || "[]");
			if (Array.isArray(parsed)) {
				fieldDefinitions.value = parsed.map((field) => ({
					name: field.name || "",
					type: field.type || "string",
					required: field.required || false,
				}));
				updateFieldDefinitions();
			}
		} catch (_e) {
			// Invalid JSON, keep current fieldDefinitions
		}
	} else {
		// Switching from visual to JSON mode
		updateFieldDefinitions(); // Update jsonValue
	}
	isJSONMode.value = !isJSONMode.value;
}

// Watch for JSON changes and update component content
watch(jsonValue, (newJsonValue) => {
	if (isJSONMode.value && component.value) {
		setContentValue(component.value.id, "inputFields", newJsonValue);
	}
});

// Reset expansion when switching modes
watch(isJSONMode, (newMode) => {
	if (!newMode) {
		isExpanded.value = false;
	}
});
</script>

<style scoped>
.BuilderSettingsArtifactAPIFieldDefinitions {
	display: flex;
	flex-direction: column;
	gap: 16px;
	padding: 24px;
}

.BuilderSettingsArtifactAPIFieldDefinitions__description {
	color: var(--wdsColorGray4);
	font-size: 14px;
	line-height: 1.4;
}

.BuilderSettingsArtifactAPIFieldDefinitions__strict-option {
	margin-top: 16px;
}

.BuilderSettingsArtifactAPIFieldDefinitions__controls {
	display: flex;
	gap: 8px;
	margin-bottom: 16px;
}

.BuilderSettingsArtifactAPIFieldDefinitions__disabled,
.BuilderSettingsArtifactAPIFieldDefinitions__empty {
	display: flex;
	flex-direction: column;
	align-items: center;
	justify-content: center;
	gap: 12px;
	padding: 32px 16px;
	border: 2px dashed var(--separatorColor);
	border-radius: 8px;
	text-align: center;
}

.BuilderSettingsArtifactAPIFieldDefinitions__disabled p,
.BuilderSettingsArtifactAPIFieldDefinitions__empty p {
	color: var(--wdsColorGray4);
	margin: 0;
}

.BuilderSettingsArtifactAPIFieldDefinitions__fields {
	display: flex;
	flex-direction: column;
	gap: 16px;
}

.BuilderSettingsArtifactAPIFieldDefinitions__field {
	border: 1px solid var(--separatorColor);
	border-radius: 8px;
	padding: 16px;
	background: var(--wdsColorGray0);
}

.BuilderSettingsArtifactAPIFieldDefinitions__field__header {
	display: flex;
	gap: 8px;
	align-items: center;
	margin-bottom: 12px;
}

.BuilderSettingsArtifactAPIFieldDefinitions__field__header .WdsButton {
	flex-shrink: 0;
	width: 32px;
	height: 32px;
	display: flex;
	align-items: center;
	justify-content: center;
}

.BuilderSettingsArtifactAPIFieldDefinitions__field__name {
	flex: 1;
	font-weight: 500;
}

.BuilderSettingsArtifactAPIFieldDefinitions__field__config {
	display: flex;
	gap: 12px;
	align-items: center;
	margin-bottom: 12px;
}

.BuilderSettingsArtifactAPIFieldDefinitions__field__type {
	min-width: 120px;
}

.BuilderSettingsArtifactAPIFieldDefinitions__provider {
	margin-top: 8px;
	padding-top: 16px;
	border-top: 1px solid var(--separatorColor);
}

.BuilderSettingsArtifactAPIFieldDefinitions__json-editor {
	border: 1px solid var(--separatorColor);
	border-radius: 8px;
	overflow: hidden;
}
</style>
