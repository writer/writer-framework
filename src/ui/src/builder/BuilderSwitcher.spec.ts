import { beforeEach, describe, expect, it, vitest, vi, Mock } from "vitest";
import { buildMockComponent, buildMockCore } from "@/tests/mocks";
import { flushPromises, shallowMount } from "@vue/test-utils";
import BuilderSwitcher from "./BuilderSwitcher.vue";
import injectionKeys from "@/injectionKeys";
import { generateBuilderManager } from "./builderManager";
import { useSecretsManager } from "@/core/useSecretsManager";

const fetchApplicationDeployment = vi.fn();
const publishApplication = vi.fn();
const fetchUserProfile = vi.fn();
const analyticsIdentify = vi.fn();

const updateApplicationMetadata = vi.fn();

vitest.mock("@/writerApi", () => ({
	WriterApi: class {
		fetchApplicationDeployment = fetchApplicationDeployment;
		publishApplication = publishApplication;
		fetchUserProfile = fetchUserProfile;
		analyticsIdentify = analyticsIdentify;
		updateApplicationMetadata = updateApplicationMetadata;
	},
}));

describe("BuilderSwitcher", () => {
	let mockCore: ReturnType<typeof buildMockCore>;
	let wfbm: ReturnType<typeof generateBuilderManager>;
	let mockUseSecretsManager: ReturnType<typeof useSecretsManager>;

	beforeEach(() => {
		mockCore = buildMockCore();
		mockCore.core.addComponent(
			buildMockComponent({
				id: "root",
				content: { appName: "APP name" },
			}),
		);
		wfbm = generateBuilderManager();

		fetchApplicationDeployment.mockReset();
		publishApplication.mockReset();
		fetchUserProfile.mockReset();
		analyticsIdentify.mockReset();

		mockUseSecretsManager = useSecretsManager(mockCore.core);
	});

	function mountBuilderSwitcher() {
		return shallowMount(BuilderSwitcher, {
			global: {
				provide: {
					[injectionKeys.core]: mockCore.core,
					[injectionKeys.builderManager]: wfbm,
					[injectionKeys.secretsManager]: mockUseSecretsManager,
				},
			},
		});
	}

	describe("non-cloud app", () => {
		beforeEach(() => {
			mockCore.writerApplication.value = undefined;
		});

		it("should not display vault button", async () => {
			const wrapper = mountBuilderSwitcher();
			await flushPromises();
			expect(
				wrapper
					.find('[data-automation-action="set-mode-vault"]')
					.exists(),
			).toBe(false);
		});
	});

	describe("cloud app", () => {
		beforeEach(() => {
			mockCore.writerApplication.value = {
				id: "app-lication-uuid",
				organizationId: "1",
			};
		});

		it("should switch to vault button", async () => {
			const wrapper = mountBuilderSwitcher();
			await flushPromises();
			wrapper
				.get('[data-automation-action="set-mode-vault"]')
				.trigger("click");
			expect(wfbm.mode.value).toBe("vault");
		});
	});
});
