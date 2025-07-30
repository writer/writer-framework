import { describe, expect, it } from "vitest";
import { nextTick } from "vue";
import BuilderSettingsProperties from "./BuilderSettingsProperties.vue";
import BuilderFieldsCheckbox from "./BuilderFieldsCheckbox.vue";
import { mount } from "@vue/test-utils";
import {
	buildMockComponent,
	buildMockCore,
	mockInstancePath,
	mockProvides,
} from "@/tests/mocks";
import injectionKeys from "@/injectionKeys";
import { generateBuilderManager } from "../builderManager";
import { flattenInstancePath } from "@/renderer/instancePath";
import WdsFieldWrapper from "@/wds/WdsFieldWrapper.vue";
import templateMap from "@/core/templateMap";
import { useSecretsManager } from "@/core/useSecretsManager";
import { FieldCategory, WriterComponentDefinitionField } from "@/writerTypes";

describe("BuilderSettingsProperties", () => {
	it.each(Object.keys(templateMap))(
		"should render settings for %s",
		async (type) => {
			const { core } = buildMockCore();
			const component = buildMockComponent({ type });
			core.addComponent(component);

			const ssbm = generateBuilderManager();
			ssbm.setSelection(
				component.id,
				flattenInstancePath(mockInstancePath),
				"click",
			);

			const wrapper = mount(BuilderSettingsProperties, {
				global: {
					provide: {
						...mockProvides,
						[injectionKeys.builderManager as symbol]: ssbm,
						[injectionKeys.core as symbol]: core,
						[injectionKeys.secretsManager as symbol]:
							useSecretsManager(core),
					},
				},
			});

			function getRenderedFieldsCount() {
				const wrapperFields =
					wrapper.findAllComponents(WdsFieldWrapper);

				const checkboxFields = wrapper.findAllComponents(
					BuilderFieldsCheckbox,
				);

				return wrapperFields.length + checkboxFields.length;
			}

			const fieldsByCategory: Record<
				FieldCategory,
				WriterComponentDefinitionField[]
			> = {
				[FieldCategory.General]: [],
				[FieldCategory.Style]: [],
				[FieldCategory.Tools]: [],
			};

			Object.values(
				// @ts-expect-error TS doesn't infer the right type for the component
				templateMap[type].writer.fields,
			).forEach((field: WriterComponentDefinitionField) => {
				switch (field.category) {
					case FieldCategory.General:
					case undefined: {
						// fields with an empty category will be also rendered in General category
						fieldsByCategory[FieldCategory.General].push(field);
						break;
					}
					case FieldCategory.Style: {
						fieldsByCategory[FieldCategory.Style].push(field);
						break;
					}
					case FieldCategory.Tools: {
						fieldsByCategory[FieldCategory.Tools].push(field);
						break;
					}
					default: {
						break;
					}
				}
			});

			const nonEmptyCategories = Object.entries(fieldsByCategory)
				.filter(([_, fields]) => fields.length > 0)
				.map(([category]) => category as FieldCategory);

			if (nonEmptyCategories.length <= 1) {
				expect(getRenderedFieldsCount()).toBe(
					Object.values(fieldsByCategory).flat().length,
				);
				return;
			}

			for (const category of nonEmptyCategories) {
				const categoryTab = wrapper.find(`button[value="${category}"]`);
				expect(categoryTab.exists()).toBe(true);

				await categoryTab.trigger("click");
				await nextTick();

				expect(getRenderedFieldsCount()).toBe(
					fieldsByCategory[category].length,
				);
			}
		},
	);
});
