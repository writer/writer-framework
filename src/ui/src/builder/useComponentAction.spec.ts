import { describe, it, expect, vi, beforeEach } from "vitest";
import { useComponentActions } from "./useComponentActions";
import { Component, Core } from "@/writerTypes.js";
import { generateBuilderManager } from "./builderManager";
import { buildMockComponent, buildMockCore } from "@/tests/mocks";

describe(useComponentActions.name, () => {
	let core: Core;
	let ssbm: ReturnType<typeof generateBuilderManager>;

	beforeEach(() => {
		ssbm = generateBuilderManager();

		core = buildMockCore().core;

		const components: Component[] = [
			{ id: "root", type: "root", position: 0 } as Component,
			{
				id: "page-id",
				type: "page",
				content: { key: "page" },
				isCodeManaged: false,
				parentId: "root",
				position: 0,
			},
			{
				id: "1",
				type: "section",
				content: { title: "Section 1" },
				isCodeManaged: false,
				parentId: "page-id",
				position: 0,
			},
			{
				id: "1.1",
				type: "section",
				content: { title: "Section 1.1" },
				isCodeManaged: false,
				parentId: "1",
				position: 0,
			},
			{
				id: "1.1.1",
				type: "section",
				content: { title: "Section 1.1.1" },
				isCodeManaged: false,
				parentId: "1.1",
				position: 0,
			},
			{
				id: "1.1.2",
				type: "section",
				content: { title: "Section 1.1.2" },
				isCodeManaged: false,
				parentId: "1.1",
				position: 1,
			},
			{
				id: "1.2",
				type: "section",
				content: { title: "Section 1.2" },
				handlers: {},
				isCodeManaged: false,
				parentId: "1",
				position: 1,
			},
			{
				id: "2",
				type: "section",
				content: { title: "Section 2" },
				handlers: {},
				isCodeManaged: false,
				parentId: "page-id",
				position: 1,
			},
		];

		components.forEach((c) => core.addComponent(c));
	});

	describe("removeComponentSubtree", () => {
		it("should delete the component in a transaction", () => {
			core.addComponent(buildMockComponent({ id: "1" }));

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

			removeComponentsSubtree("1", "2");

			expect(core.sendComponentUpdate).toHaveBeenCalledOnce();
			expect(openMutationTransaction).toHaveBeenNthCalledWith(
				1,
				"delete-1,2",
				"Delete",
			);
		});
	});

	describe("components movements", () => {
		it("should go to the parent", () => {
			const { isGoToParentAllowed, goToParent } = useComponentActions(
				core,
				ssbm,
			);
			expect(isGoToParentAllowed("root")).toBe(false);
			expect(isGoToParentAllowed("1")).toBe(true);
			expect(isGoToParentAllowed("1.1")).toBe(true);

			goToParent("1.1");
			expect(ssbm.firstSelectedId.value).toBe("1");
		});

		it("should go to the child", () => {
			const { isGoToChildAllowed, goToChild } = useComponentActions(
				core,
				ssbm,
			);
			expect(isGoToChildAllowed("root")).toBe(true);
			expect(isGoToChildAllowed("1")).toBe(true);
			expect(isGoToChildAllowed("1.1.1")).toBe(false);

			goToChild("1");
			expect(ssbm.firstSelectedId.value).toBe("1.1");
		});

		it("should go to the previous sibling", () => {
			const { isGoToPrevSiblingAllowed, goToPrevSibling } =
				useComponentActions(core, ssbm);
			expect(isGoToPrevSiblingAllowed("root")).toBe(false);
			expect(isGoToPrevSiblingAllowed("1")).toBe(false);
			expect(isGoToPrevSiblingAllowed("1.1")).toBe(false);
			expect(isGoToPrevSiblingAllowed("1.2")).toBe(true);

			goToPrevSibling("1.2");
			expect(ssbm.firstSelectedId.value).toBe("1.1");
		});

		it("should go to the next sibling", () => {
			const { isGoToNextSiblingAllowed, goToNextSibling } =
				useComponentActions(core, ssbm);
			expect(isGoToNextSiblingAllowed("root")).toBe(false);
			expect(isGoToNextSiblingAllowed("1")).toBe(true);
			expect(isGoToNextSiblingAllowed("1.1")).toBe(true);
			expect(isGoToNextSiblingAllowed("1.2")).toBe(false);

			goToNextSibling("1.1");
			expect(ssbm.firstSelectedId.value).toBe("1.2");

			goToNextSibling("1");
			expect(ssbm.firstSelectedId.value).toBe("2");
		});
	});
});
