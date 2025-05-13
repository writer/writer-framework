import { vi, vitest, describe, beforeEach, it, expect } from "vitest";
import { useWriterTracking } from "./useWriterTracking";
import { buildMockComponent, buildMockCore } from "@/tests/mocks";
import { defineComponent } from "vue";
import { flushPromises, shallowMount } from "@vue/test-utils";

const analyticsIdentify = vi.fn();
const analyticsTrack = vi.fn();

vitest.mock("@/writerApi", () => ({
	WriterApi: class {
		analyticsIdentify = analyticsIdentify;
		analyticsTrack = analyticsTrack;
	},
}));

vitest.mock("@/utils/writerCloudEnvConfig", () => ({
	getWriterCloudEnvConfig: vi.fn().mockResolvedValue({}),
}));

describe(useWriterTracking.name, () => {
	let mockCore: ReturnType<typeof buildMockCore>;

	const Wrapper = defineComponent({
		setup() {
			return useWriterTracking(mockCore.core);
		},
		template: `<div></div>`,
	});

	beforeEach(() => {
		mockCore = buildMockCore();
		analyticsIdentify.mockReset();
		analyticsTrack.mockReset();
	});

	describe("in run mode without cloud vars", () => {
		beforeEach(() => {
			mockCore.mode.value = "run";
			mockCore.writerApplication.value = undefined;
		});

		it("should not track event ", async () => {
			mockCore.mode.value = "run";
			const wrapper = shallowMount(Wrapper);
			await flushPromises();
			await wrapper.vm.track("ui_block_added");

			expect(analyticsTrack).not.toHaveBeenCalled();
		});
	});

	describe("in run mode with cloud vars", () => {
		beforeEach(() => {
			mockCore.mode.value = "run";
			mockCore.writerApplication.value = { id: "1", organizationId: "2" };
		});

		it("should not track event ", async () => {
			mockCore.mode.value = "run";
			const wrapper = shallowMount(Wrapper);
			await flushPromises();
			await wrapper.vm.track("ui_block_added");

			expect(analyticsTrack).not.toHaveBeenCalled();
		});
	});

	describe("in edit mode without cloud vars", () => {
		beforeEach(() => {
			mockCore.mode.value = "edit";
			mockCore.writerApplication.value = undefined;
		});

		it("should not track event", async () => {
			const wrapper = shallowMount(Wrapper);
			await flushPromises();
			await wrapper.vm.track("ui_block_added");

			expect(analyticsTrack).not.toHaveBeenCalled();
		});
	});

	describe("in edit mode with cloud vars", () => {
		beforeEach(() => {
			mockCore.mode.value = "edit";
			mockCore.writerApplication.value = { organizationId: "1", id: "2" };
		});

		it("should track", async () => {
			const wrapper = shallowMount(Wrapper);
			await flushPromises();
			await wrapper.vm.track("ui_block_added");

			expect(analyticsTrack).toHaveBeenCalledExactlyOnceWith(
				"[AgentEditor] ui_block_added",
				{
					writerApplicationId: "2",
					writerOrganizationId: "1",
				},
			);
		});

		it("should get component information", async () => {
			mockCore.mode.value = "edit";
			mockCore.writerApplication.value = { organizationId: "1", id: "2" };

			mockCore.core.addComponent(
				buildMockComponent({ id: "1", type: "button" }),
			);

			const wrapper = shallowMount(Wrapper);
			await flushPromises();
			await wrapper.vm.track("ui_block_added", { componentId: "1" });

			expect(analyticsTrack).toHaveBeenCalledExactlyOnceWith(
				"[AgentEditor] ui_block_added",
				{
					component: {
						category: "Other",
						name: "Button",
					},
					writerApplicationId: "2",
					writerOrganizationId: "1",
				},
			);
		});
	});
});
