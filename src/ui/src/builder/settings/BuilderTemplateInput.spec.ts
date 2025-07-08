import { beforeEach, describe, it, expect } from "vitest";
import { flushPromises, mount } from "@vue/test-utils";
import BuilderTemplateInput from "./BuilderTemplateInput.vue";
import { buildMockCore, buildMockSecretsManager } from "@/tests/mocks";
import injectionKeys from "@/injectionKeys";
import { ExtractPropTypes } from "vue";
import BuilderStateSelectorDropdown from "../stateDropdown/BuilderStateSelectorDropdown.vue";
import WdsDropdownMenuItem from "@/wds/WdsDropdownMenuItem.vue";
import BuilderTemplateInputInput from "./BuilderTemplateInputInput.vue";

describe.skip("BuilderTemplateInput", () => {
	let mockCore: ReturnType<typeof buildMockCore>;
	let mockSecretManager: ReturnType<typeof buildMockSecretsManager>;

	beforeEach(() => {
		mockCore = buildMockCore();
		mockSecretManager = buildMockSecretsManager(mockCore.core);
		mockCore.userStateInitial.value = {
			obj: {
				a: 1,
				b: 1,
			},
			text: "foo",
			array: ["a", "b", "c"],
		};
	});

	function mountWrapper(
		props: ExtractPropTypes<typeof BuilderTemplateInput> = {
			type: "template",
			value: "",
		},
	) {
		return mount(BuilderTemplateInput, {
			props,
			global: {
				provide: {
					[injectionKeys.core]: mockCore.core,
					[injectionKeys.secretsManager]:
						mockSecretManager.secretsManager,
				},
			},
		});
	}

	describe("in template mode", () => {
		it.each(["@", "@{"])('should autocomplete with "%s"', async (input) => {
			const wrapper = mountWrapper({
				value: input,
			});

			wrapper
				.getComponent(BuilderTemplateInputInput)
				.vm.$emit("input", { target: { value: input } });
			await flushPromises();

			const options = wrapper
				.getComponent(BuilderStateSelectorDropdown)
				.findAllComponents(WdsDropdownMenuItem);

			expect(options).toHaveLength(5);

			await options.at(0).trigger("click");

			await flushPromises();

			expect(wrapper.emitted("update:value").at(-1)).toStrictEqual([
				"@{array}",
			]);
		});

		it("should autocomplete object items", async () => {
			const wrapper = mountWrapper();

			wrapper
				.getComponent(BuilderTemplateInputInput)
				.vm.$emit("input", { target: { value: "@{obj." } });
			await flushPromises();

			const dropdown = wrapper.getComponent(BuilderStateSelectorDropdown);
			expect(dropdown.props("query")).toBe("obj.");

			const options = dropdown.findAllComponents(WdsDropdownMenuItem);
			expect(options).toHaveLength(2);

			await options.at(0).trigger("click");

			await flushPromises();

			expect(wrapper.emitted("update:value").at(-1)).toStrictEqual([
				"@{obj.a}",
			]);
		});

		it.only("should autocomplete with templating", async () => {
			const wrapper = mountWrapper({
				value: "foo @{tex",
			});

			wrapper
				.getComponent(BuilderTemplateInputInput)
				.vm.$emit("input", { target: { value: "foo @{tex" } });
			await flushPromises();

			const dropdown = wrapper.getComponent(BuilderStateSelectorDropdown);
			expect(dropdown.props("query")).toBe("tex");

			const options = dropdown.findAllComponents(WdsDropdownMenuItem);
			expect(options).toHaveLength(1);

			await options.at(0).trigger("click");

			await flushPromises();

			expect(wrapper.emitted("update:value").at(-1)).toStrictEqual([
				"foo @{text}",
			]);
		});

		it("should autocomplete vault", async () => {
			mockSecretManager.secrets.value = {
				GOOGLE_API_KEY: "foo",
			};
			const wrapper = mountWrapper();

			await wrapper.get("input").setValue("@{vault.");

			const dropdown = wrapper.getComponent(BuilderStateSelectorDropdown);
			expect(dropdown.props("query")).toBe("vault.");

			const options = dropdown.findAllComponents(WdsDropdownMenuItem);
			expect(options).toHaveLength(1);

			expect(options.at(0).attributes("data-automation-key")).toBe(
				"vault.GOOGLE_API_KEY",
			);

			await options.at(0).trigger("click");

			await flushPromises();

			expect(wrapper.emitted("update:value").at(-1)).toStrictEqual([
				"@{vault.GOOGLE_API_KEY}",
			]);
		});

		it("should not autocomplete vault when empty", async () => {
			mockSecretManager.secrets.value = {};
			const wrapper = mountWrapper();

			await wrapper.get("input").setValue("@{vault.");

			const dropdown = wrapper.getComponent(BuilderStateSelectorDropdown);
			const options = dropdown.findAllComponents(WdsDropdownMenuItem);

			expect(options).toHaveLength(0);
		});
	});

	describe("in state mode", () => {
		it("should autocomplete object items", async () => {
			const wrapper = mountWrapper({
				type: "state",
				value: "hello",
			});

			await wrapper.get("input").setValue("obj.");

			const dropdown = wrapper.getComponent(BuilderStateSelectorDropdown);
			expect(dropdown.props("query")).toBe("obj.");

			const options = dropdown.findAllComponents(WdsDropdownMenuItem);
			expect(options).toHaveLength(2);

			expect(options.at(0).attributes("data-automation-key")).toBe(
				"obj.a",
			);
			expect(options.at(1).attributes("data-automation-key")).toBe(
				"obj.b",
			);

			await options.at(0).trigger("click");

			await flushPromises();

			expect(wrapper.emitted("update:value").at(-1)).toStrictEqual([
				"obj.a",
			]);
		});

		it("should not autocomplete vault", async () => {
			mockSecretManager.secrets.value = {
				GOOGLE_API_KEY: "foo",
			};
			const wrapper = mountWrapper({
				type: "state",
				value: "hello",
				hideDropdownSecrets: true,
			});

			await wrapper.get("input").setValue("vault.");

			const dropdown = wrapper.getComponent(BuilderStateSelectorDropdown);
			expect(dropdown.props("query")).toBe("vault.");

			const options = dropdown.findAllComponents(WdsDropdownMenuItem);
			expect(options).toHaveLength(0);
		});
	});
});
