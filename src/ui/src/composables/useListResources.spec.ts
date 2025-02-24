import { afterAll, beforeEach, describe, expect, it, Mock, vi } from "vitest";
import { useListResources } from "./useListResources";
import { buildMockCore } from "@/tests/mocks";

describe(useListResources.name, () => {
	const resources = [
		{ id: 1, name: "one" },
		{ id: 2, name: "two" },
	];
	let core: ReturnType<typeof buildMockCore>["core"];
	let localStorage: { getItem: Mock; setItem: Mock; removeItem: Mock };

	beforeEach(() => {
		localStorage = {
			getItem: vi.fn().mockReturnValue(JSON.stringify(resources)),
			setItem: vi.fn(),
			removeItem: vi.fn(),
		};

		vi.stubGlobal("localStorage", localStorage);

		core = buildMockCore().core;
	});

	afterAll(() => {
		vi.restoreAllMocks();
	});

	it("should load the resources", async () => {
		const loadedResources = [...resources, { id: 3, name: "three" }];
		vi.spyOn(core, "sendListResourcesRequest").mockResolvedValue(
			loadedResources,
		);

		const { load, data } = useListResources(core, "graphs");

		expect(data.value).toStrictEqual(resources);

		await load();

		expect(data.value).toStrictEqual(loadedResources);
	});

	it("should handle error", async () => {
		const apiError = new Error("ooops");
		vi.spyOn(core, "sendListResourcesRequest").mockRejectedValue(apiError);

		const { load, data, error } = useListResources(core, "graphs");

		expect(data.value).toStrictEqual(resources);

		await load();

		expect(data.value).toStrictEqual([]);
		expect(error.value).toStrictEqual(apiError);
	});
});
