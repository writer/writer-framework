import { beforeEach, describe, expect, it, vitest, vi, Mock } from "vitest";
import { buildMockCore } from "@/tests/mocks";
import { flushPromises, shallowMount } from "@vue/test-utils";
import BuilderHeader from "./BuilderHeader.vue";
import WdsModal from "@/wds/WdsModal.vue";
import injectionKeys from "@/injectionKeys";
import { generateBuilderManager } from "./builderManager";

const fetchApplicationDeployment = vi.fn();
const publishApplication = vi.fn();
const fetchUserProfile = vi.fn();

vitest.mock("@/writerApi", () => ({
	WriterApi: class {
		fetchApplicationDeployment = fetchApplicationDeployment;
		publishApplication = publishApplication;
		fetchUserProfile = fetchUserProfile;
	},
}));

describe("BuilderHeader", () => {
	let mockCore: ReturnType<typeof buildMockCore>;
	let wfbm: ReturnType<typeof generateBuilderManager>;

	beforeEach(() => {
		mockCore = buildMockCore();
		wfbm = generateBuilderManager();

		fetchApplicationDeployment.mockReset();
		publishApplication.mockReset();
		fetchUserProfile.mockReset();
	});

	describe("non-cloud app", () => {
		beforeEach(() => {
			mockCore.writerApplication.value = undefined;
		});

		it("should not display deploy button", async () => {
			const wrapper = shallowMount(BuilderHeader, {
				global: {
					provide: {
						[injectionKeys.core]: mockCore.core,
						[injectionKeys.builderManager]: wfbm,
					},
				},
			});
			await flushPromises();
			expect(
				wrapper.find('[data-automation-key="deploy"]').exists(),
			).toBe(false);
		});
	});

	describe("cloud app", () => {
		let windowOpen: Mock;
		beforeEach(() => {
			mockCore.writerApplication.value = {
				id: "app-lication-uuid",
				organizationId: "1",
			};
			windowOpen = vi.fn();
			window.open = windowOpen;
		});

		it("should display deploy button for undeployed app", async () => {
			fetchApplicationDeployment.mockResolvedValue({
				lastDeployedAt: null,
				writer: {},
			});

			const wrapper = shallowMount(BuilderHeader, {
				global: {
					provide: {
						[injectionKeys.core]: mockCore.core,
						[injectionKeys.builderManager]: wfbm,
					},
				},
			});
			await flushPromises();

			const deployBtn = wrapper.get('[data-automation-key="deploy"]');
			expect(deployBtn.attributes("data-writer-tooltip")).toBeUndefined();
		});

		it("should display last deploy", async () => {
			fetchApplicationDeployment.mockResolvedValue({
				lastDeployedAt: "2025-01-02T03:04:05",
				writer: {},
			});

			const wrapper = shallowMount(BuilderHeader, {
				global: {
					provide: {
						[injectionKeys.core]: mockCore.core,
						[injectionKeys.builderManager]: wfbm,
					},
				},
			});
			await flushPromises();

			const deployBtn = wrapper.get('[data-automation-key="deploy"]');
			expect(deployBtn.attributes("data-writer-tooltip")).toBe(
				"Editor Last saved Thursday, January 2, 2025 at 3:04 AM",
			);
		});

		it("should open the modal on open", async () => {
			fetchApplicationDeployment.mockResolvedValue({
				lastDeployedAt: "2025-01-02T03:04:05",
				applicationVersionData: {
					id: 2,
				},
				applicationVersion: {
					id: 3,
				},
				writer: {},
			});

			const wrapper = shallowMount(BuilderHeader, {
				global: {
					provide: {
						[injectionKeys.core]: mockCore.core,
						[injectionKeys.builderManager]: wfbm,
					},
				},
			});
			await flushPromises();

			await wrapper
				.get('[data-automation-key="deploy"]')
				.trigger("click");
			await flushPromises();

			expect(wrapper.findComponent(WdsModal).exists()).toBe(false);
		});
	});
});
