import {
	beforeEach,
	describe,
	it,
	vi,
	expect,
	beforeAll,
	afterAll,
	MockInstance,
} from "vitest";
import { useApplicationCloud } from "./useApplicationCloud";
import { buildMockComponent, buildMockCore } from "@/tests/mocks";
import { flushPromises, mount } from "@vue/test-utils";
import { defineComponent } from "vue";

describe(useApplicationCloud.name, () => {
	let fetch: MockInstance;
	let mockCore: ReturnType<typeof buildMockCore>;

	const component = defineComponent({
		setup() {
			const { name } = useApplicationCloud(mockCore.core);
			const updateName = (value: string) => (name.value = value);
			return { updateName };
		},
		template: "<div></div>",
	});

	beforeAll(() => {
		vi.useFakeTimers();
	});

	afterAll(() => {
		vi.useRealTimers();
	});

	beforeEach(() => {
		mockCore = buildMockCore();

		mockCore.core.addComponent(
			buildMockComponent({
				id: "root",
				content: { appName: "APP name" },
			}),
		);

		fetch = vi.spyOn(global, "fetch").mockResolvedValue({
			ok: true,
			json: async () => ({ username: "new name" }),
		} as Response);
	});

	describe("cloud app", () => {
		beforeEach(() => {
			mockCore.featureFlags.value = ["writerCloud"];
		});

		it("should fetch the name on start", async () => {
			mount(component);
			await flushPromises();

			expect(fetch).toHaveBeenCalledTimes(1);

			expect(mockCore.core.getComponentById("root").content.appName).toBe(
				"new name",
			);
		});

		it("should handle app name update", async () => {
			const wrapper = mount(component);
			await flushPromises();
			expect(fetch).toHaveBeenCalledTimes(1);

			wrapper.vm.updateName("hello");
			await flushPromises();

			vi.advanceTimersByTime(3_000);
			await flushPromises();
			expect(fetch).toHaveBeenCalledTimes(2);

			expect(mockCore.core.getComponentById("root").content.appName).toBe(
				"hello",
			);
		});
	});

	describe("not-cloud app", () => {
		it("should handle app name update", async () => {
			const wrapper = mount(component);
			await flushPromises();
			expect(fetch).not.toHaveBeenCalled();
			wrapper.vm.updateName("new name");
			await flushPromises();

			vi.advanceTimersByTime(3_000);
			await flushPromises();
			expect(fetch).not.toHaveBeenCalled();

			expect(mockCore.core.getComponentById("root").content.appName).toBe(
				"new name",
			);
		});
	});
});
