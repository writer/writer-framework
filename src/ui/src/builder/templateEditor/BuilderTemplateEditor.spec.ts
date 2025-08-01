import { describe, it, expect, beforeEach } from "vitest";
import { flushPromises, mount } from "@vue/test-utils";
import { useSecretsManager } from "@/core/useSecretsManager";
import injectionKeys from "@/injectionKeys";
import { buildMockCore } from "@/tests/mocks";
import { generateBuilderManager } from "../builderManager";
import BuilderTemplateEditor from "./BuilderTemplateEditor.vue";

describe("BuilderTemplateEditor", () => {
	let mockCore: ReturnType<typeof buildMockCore>;
	let wfbm: ReturnType<typeof generateBuilderManager>;
	let mockUseSecretsManager: ReturnType<typeof useSecretsManager>;

	beforeEach(() => {
		mockCore = buildMockCore();
		mockCore.userState.value = {
			var: "1",
		};
		wfbm = generateBuilderManager();

		mockUseSecretsManager = useSecretsManager(mockCore.core);
	});

	async function mountWrapper(
		props: InstanceType<typeof BuilderTemplateEditor>["$props"],
	) {
		const wrapper = mount(BuilderTemplateEditor, {
			props,
			global: {
				provide: {
					[injectionKeys.core]: mockCore.core,
					[injectionKeys.builderManager]: wfbm,
					[injectionKeys.secretsManager]: mockUseSecretsManager,
				},
			},
		});
		await flushPromises();
		return wrapper;
	}

	describe("single line", () => {
		it("should render var", async () => {
			const wrapper = await mountWrapper({
				modelValue: "This is a single line with a @{var}!",
			});
			expect(
				wrapper.get(".BuilderTemplateEditorInterpolation").text(),
			).toBe("@{var}");
			expect(wrapper.find("br").exists()).toBeFalsy();

			expect(wrapper.element).toMatchSnapshot();
		});
	});

	describe("multi line", () => {
		it("should render var", async () => {
			const wrapper = await mountWrapper({
				modelValue: "This is a single line with a @{var}!",
				multiline: true,
			});

			expect(
				wrapper.get(".BuilderTemplateEditorInterpolation").text(),
			).toBe("@{var}");
			expect(wrapper.find("br").exists()).toBeFalsy();

			expect(wrapper.element).toMatchSnapshot();
		});

		it("should render multiline", async () => {
			const wrapper = await mountWrapper({
				modelValue: [
					"This is a single line with a @{var}!",
					"with a @{second} line",
				].join("\n"),
				multiline: true,
			});

			expect(
				wrapper.get(".BuilderTemplateEditorInterpolation").text(),
			).toBe("@{var}");
			expect(wrapper.findAll("br")).toHaveLength(1);

			expect(wrapper.element).toMatchSnapshot();
		});

		it("should render multiples multiline", async () => {
			const wrapper = await mountWrapper({
				modelValue: ["", "", "", "line 3", "", "line 5"].join("\n"),
				multiline: true,
			});

			expect(wrapper.findAll("br")).toHaveLength(5);

			expect(wrapper.element).toMatchSnapshot();
		});
	});
});
