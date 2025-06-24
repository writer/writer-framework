import { beforeEach, describe, it, expect } from "vitest";
import { flushPromises, mount } from "@vue/test-utils";
import BuilderTemplateInput from "./BuilderTemplateInput.vue";
import { buildMockCore, buildMockSecretsManager } from "@/tests/mocks";
import injectionKeys from "@/injectionKeys";
import { ExtractPropTypes } from "vue";

describe("BuilderTemplateInput", () => {
	let mockCore: ReturnType<typeof buildMockCore>;
	let mockSecretManager: ReturnType<typeof buildMockSecretsManager>;

	beforeEach(() => {
		mockCore = buildMockCore();
		mockSecretManager = buildMockSecretsManager(mockCore.core);
		mockCore.userState.value = {
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
				directives: {
					"capture-tabs": {},
				},
			},
		});
	}

	describe("in template mode", () => {
		it.each(["@", "@{"])('should autocomplete with "%s"', async (input) => {
			const wrapper = mountWrapper();

			await wrapper.get("input").setValue(input);

			const options = wrapper
				.get(".fieldStateAutocomplete")
				.findAll(".fieldStateAutocompleteOption");

			expect(options).toHaveLength(5);
			expect(options.at(0).get(".prop").text()).toBe("array");
			expect(options.at(0).get(".type").text()).toBe("object");
			expect(options.at(1).get(".prop").text()).toBe("obj");
			expect(options.at(1).get(".type").text()).toBe("object");
			expect(options.at(2).get(".prop").text()).toBe("obj.a");
			expect(options.at(2).get(".type").text()).toBe("number");
			expect(options.at(3).get(".prop").text()).toBe("obj.b");
			expect(options.at(4).get(".prop").text()).toBe("text");
			expect(options.at(4).get(".type").text()).toBe("string");

			await options.at(0).trigger("click");

			await flushPromises();

			expect(wrapper.emitted("update:value").at(-1)).toStrictEqual([
				"@{array}",
			]);
		});

		it("should autocomplete an array items", async () => {
			const wrapper = mountWrapper();

			await wrapper.get("input").setValue("@{array.");

			const options = wrapper
				.get(".fieldStateAutocomplete")
				.findAll(".fieldStateAutocompleteOption");

			expect(options).toHaveLength(3);
			expect(options.at(0).get(".prop").text()).toBe("0");
			expect(options.at(1).get(".prop").text()).toBe("1");
			expect(options.at(2).get(".prop").text()).toBe("2");

			await options.at(0).trigger("click");

			await flushPromises();

			expect(wrapper.emitted("update:value").at(-1)).toStrictEqual([
				"@{array.0}",
			]);
		});

		it("should autocomplete object items", async () => {
			const wrapper = mountWrapper();

			await wrapper.get("input").setValue("@{obj.");

			const options = wrapper
				.get(".fieldStateAutocomplete")
				.findAll(".fieldStateAutocompleteOption");

			expect(options).toHaveLength(2);
			expect(options.at(0).get(".prop").text()).toBe("a");
			expect(options.at(1).get(".prop").text()).toBe("b");

			await options.at(0).trigger("click");

			await flushPromises();

			expect(wrapper.emitted("update:value").at(-1)).toStrictEqual([
				"@{obj.a}",
			]);
		});

		it("should autocomplete with templating", async () => {
			const wrapper = mountWrapper();

			await wrapper.get("input").setValue("foo @{tex");

			const options = wrapper
				.get(".fieldStateAutocomplete")
				.findAll(".fieldStateAutocompleteOption");

			expect(options).toHaveLength(1);
			expect(options.at(0).get(".prop").text()).toBe("text");

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

			const options = wrapper
				.get(".fieldStateAutocomplete")
				.findAll(".fieldStateAutocompleteOption");

			expect(options).toHaveLength(1);
			expect(options.at(0).get(".prop").text()).toBe("GOOGLE_API_KEY");
			expect(options.at(0).get(".type").text()).toBe("string");

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

			expect(
				wrapper.find(".fieldStateAutocomplete").exists(),
			).toBeFalsy();
		});
	});

	describe("in state mode", () => {
		it("should autocomplete an array items", async () => {
			const wrapper = mountWrapper({
				type: "state",
				value: "",
			});

			await wrapper.get("input").setValue("array.");

			const options = wrapper
				.get(".fieldStateAutocomplete")
				.findAll(".fieldStateAutocompleteOption");

			expect(options).toHaveLength(3);
			expect(options.at(0).get(".prop").text()).toBe("0");
			expect(options.at(1).get(".prop").text()).toBe("1");
			expect(options.at(2).get(".prop").text()).toBe("2");

			await options.at(0).trigger("click");

			await flushPromises();

			expect(wrapper.emitted("update:value").at(-1)).toStrictEqual([
				"array.0",
			]);
		});

		it("should autocomplete object items", async () => {
			const wrapper = mountWrapper({
				type: "state",
				value: "",
			});

			await wrapper.get("input").setValue("obj.");

			const options = wrapper
				.get(".fieldStateAutocomplete")
				.findAll(".fieldStateAutocompleteOption");

			expect(options).toHaveLength(2);
			expect(options.at(0).get(".prop").text()).toBe("a");
			expect(options.at(1).get(".prop").text()).toBe("b");

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
			const wrapper = mountWrapper();

			await wrapper.get("input").setValue("vault.");

			expect(
				wrapper.find(".fieldStateAutocomplete").exists(),
			).toBeFalsy();
		});
	});
});
