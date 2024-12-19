import { describe, it, expect, vi, beforeEach } from "vitest";
import { useComponentActions } from "./useComponentActions";
import { Core } from "@/writerTypes.js";
import { generateBuilderManager } from "./builderManager";

describe(useComponentActions.name, () => {
	let core: Core;
	let ssbm: ReturnType<typeof generateBuilderManager>;

	beforeEach(() => {
		ssbm = generateBuilderManager();

		// @ts-expect-error we mock only necessary functions
		core = {
			getComponentById: vi
				.fn()
				.mockImplementation((id: string) => ({ id })),
			getComponents: vi.fn().mockReturnValue([]),
			deleteComponent: vi.fn(),
			sendComponentUpdate: vi.fn(),
		};
	});

	describe("removeComponentSubtree", () => {
		it("should delete the component in a transaction", () => {
			const { removeComponentSubtree } = useComponentActions(core, ssbm);

			const openMutationTransaction = vi.spyOn(
				ssbm,
				"openMutationTransaction",
			);

			removeComponentSubtree("1");

			expect(core.sendComponentUpdate).toHaveBeenCalledOnce();
			expect(openMutationTransaction).toHaveBeenNthCalledWith(
				1,
				"delete-1",
				"Delete",
			);
		});
	});

	describe("removeComponentsSubtree", () => {
		it("should delete the component in a transaction", () => {
			const { removeComponentsSubtree } = useComponentActions(core, ssbm);

			const openMutationTransaction = vi.spyOn(
				ssbm,
				"openMutationTransaction",
			);

			removeComponentsSubtree("1", "2", "3");

			expect(core.sendComponentUpdate).toHaveBeenCalledOnce();
			expect(openMutationTransaction).toHaveBeenNthCalledWith(
				1,
				"delete-1,2,3",
				"Delete",
			);
		});
	});
});
