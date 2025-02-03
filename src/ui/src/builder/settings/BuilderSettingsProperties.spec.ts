import { describe, expect, it } from "vitest";
import BuilderSettingsProperties from "./BuilderSettingsProperties.vue";
import { shallowMount } from "@vue/test-utils";
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

describe("BuilderSettingsProperties", () => {
	it.each(Object.keys(templateMap))(
		"should render settings for %s",
		(type) => {
			const { core } = buildMockCore();
			const component = buildMockComponent({ type });
			core.addComponent(component);

			const ssbm = generateBuilderManager();
			ssbm.setSelection(
				component.id,
				flattenInstancePath(mockInstancePath),
				"click",
			);

			const wrapper = shallowMount(BuilderSettingsProperties, {
				global: {
					provide: {
						...mockProvides,
						[injectionKeys.builderManager as symbol]: ssbm,
						[injectionKeys.core as symbol]: core,
					},
				},
			});

			// check that each fields is renderer
			expect(wrapper.findAllComponents(WdsFieldWrapper)).toHaveLength(
				// @ts-expect-error TS doesn't infer the right type for the component
				Object.keys(templateMap[type].writer.fields).length,
			);
		},
	);
});
