import { describe, it, expect } from "vitest";
import { buildMockCore } from "./mocks";

describe("canEditAgent gating", () => {
	function setup() {
		const { core, featureFlags, writerApplication } = buildMockCore();
		return { core, featureFlags, writerApplication };
	}

	it("allows editing outside of Writer cloud", () => {
		const { core, featureFlags } = setup();
		featureFlags.value = ["beforeDeprecationCutoffAbv2"];
		expect(core.canEditAgent.value).toBe(true);
	});

	it("does not block editing when no deprecation flag is active", () => {
		const { core, featureFlags, writerApplication } = setup();
		writerApplication.value = {
			id: "app-1",
			organizationId: "1",
			isOrganizationAdmin: false,
			canEdit: false,
		};
		featureFlags.value = [];
		expect(core.canEditAgent.value).toBe(true);
	});

	it.each(["beforeDeprecationCutoffAbv2", "afterDeprecationCutoffAbv2"])(
		"blocks editing for a non-admin without edit access when %s is active",
		(flag) => {
			const { core, featureFlags, writerApplication } = setup();
			writerApplication.value = {
				id: "app-1",
				organizationId: "1",
				isOrganizationAdmin: false,
				canEdit: false,
			};
			featureFlags.value = [flag];
			expect(core.canEditAgent.value).toBe(false);
		},
	);

	it("allows editing for an org admin when gating is active", () => {
		const { core, featureFlags, writerApplication } = setup();
		writerApplication.value = {
			id: "app-1",
			organizationId: "1",
			isOrganizationAdmin: true,
			canEdit: false,
		};
		featureFlags.value = ["beforeDeprecationCutoffAbv2"];
		expect(core.canEditAgent.value).toBe(true);
	});

	it("allows editing when canEdit is granted and gating is active", () => {
		const { core, featureFlags, writerApplication } = setup();
		writerApplication.value = {
			id: "app-1",
			organizationId: "1",
			isOrganizationAdmin: false,
			canEdit: true,
		};
		featureFlags.value = ["afterDeprecationCutoffAbv2"];
		expect(core.canEditAgent.value).toBe(true);
	});
});
