import {
	beforeEach,
	describe,
	it,
	vi,
	expect,
	beforeAll,
	afterAll,
} from "vitest";
import { useApplicationName } from "./useApplicationName";
import { buildMockComponent, buildMockCore } from "@/tests/mocks";
import { flushPromises, mount } from "@vue/test-utils";
import { defineComponent } from "vue";

describe(useApplicationName.name, () => {
	let mockCore: ReturnType<typeof buildMockCore>;

	const component = defineComponent({
		setup() {
			const name = useApplicationName(mockCore.core);
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
	});

	it("should make an API call to update the application name", async () => {
		const wrapper = mount(component);
		const fetch = vi
			.spyOn(global, "fetch")
			.mockResolvedValue(new Response());
		wrapper.vm.updateName("new name");
		await flushPromises();

		vi.advanceTimersByTime(3_000);
		await flushPromises();
		expect(fetch).toHaveBeenCalledTimes(1);
	});
});
