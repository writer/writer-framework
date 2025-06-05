import { beforeEach, describe, it, vitest, vi, expect } from "vitest";
import { buildMockComponent, buildMockCore } from "@/tests/mocks";
import { flushPromises, shallowMount } from "@vue/test-utils";
import BuilderVault from "./BuilderVault.vue";
import injectionKeys from "@/injectionKeys";
import { generateBuilderManager } from "./builderManager";
import { useSecretsManager } from "@/core/useSecretsManager";

const fetchUserProfile = vi.fn();
const analyticsIdentify = vi.fn();

const updateApplicationMetadata = vi.fn();

vitest.mock("@/writerApi", () => ({
	WriterApi: class {
		fetchUserProfile = fetchUserProfile;
		analyticsIdentify = analyticsIdentify;
		updateApplicationMetadata = updateApplicationMetadata;
	},
}));

describe("BuilderVault", () => {
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

		fetchUserProfile.mockReset();
		analyticsIdentify.mockReset();

		mockUseSecretsManager = useSecretsManager(mockCore.core);

		mockCore.writerApplication.value = {
			id: "app-lication-uuid",
			organizationId: "1",
		};
	});

	function mountBuilderVault() {
		return shallowMount(BuilderVault, {
			global: {
				provide: {
					[injectionKeys.core]: mockCore.core,
					[injectionKeys.builderManager]: wfbm,
					[injectionKeys.secretsManager]: mockUseSecretsManager,
				},
			},
		});
	}

	it("should mount the component", async () => {
		const wrapper = mountBuilderVault();
		await flushPromises();
		expect(wrapper.exists()).toBe(true);
	});
});
