import { describe, it, expect, vi, beforeEach } from "vitest";
import { useComponentActions } from "./useComponentActions";
import { Component } from "@/writerTypes.js";
import { generateBuilderManager } from "./builderManager";
import { buildMockComponent, buildMockCore } from "@/tests/mocks";

describe(useComponentActions.name, () => {
	let mockCore: ReturnType<typeof buildMockCore>;
	let wfbm: ReturnType<typeof generateBuilderManager>;

	beforeEach(() => {
		wfbm = generateBuilderManager();

		mockCore = buildMockCore();

		const components: Component[] = [
			{ id: "root", type: "root", position: 0 } as Component,
			{
				id: "blueprints_root",
				type: "blueprints_root",
				position: 0,
			} as Component,
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
			{
				id: "blueprints_blueprint-id",
				type: "blueprints_blueprint",
				content: {},
				handlers: {},
				isCodeManaged: false,
				parentId: "blueprints_root",
				position: 1,
			},
		];

		components.forEach((c) => mockCore.core.addComponent(c));
	});

	describe("isDeleteAllowed", () => {
		it("should handle UI components", () => {
			const { isDeleteAllowed } = useComponentActions(
				mockCore.core,
				wfbm,
			);
			expect(isDeleteAllowed("root")).toBeFalsy();
			expect(isDeleteAllowed("page-id")).toBeTruthy();
		});

		it("should handle blueprint components", () => {
			const { isDeleteAllowed } = useComponentActions(
				mockCore.core,
				wfbm,
			);
			expect(isDeleteAllowed("blueprints_root")).toBeFalsy();
			expect(isDeleteAllowed("blueprints_blueprint-id")).toBeTruthy();
		});
	});

	describe("removeComponentSubtree", () => {
		it("should delete the component in a transaction", () => {
			mockCore.core.addComponent(buildMockComponent({ id: "1" }));

			const { removeComponentSubtree } = useComponentActions(
				mockCore.core,
				wfbm,
			);

			const openMutationTransaction = vi.spyOn(
				wfbm,
				"openMutationTransaction",
			);

			removeComponentSubtree("1");

			expect(mockCore.core.sendComponentUpdate).toHaveBeenCalledOnce();
			expect(openMutationTransaction).toHaveBeenNthCalledWith(
				1,
				"delete-1",
				"Delete",
			);
		});
	});

	describe("removeComponentsSubtree", () => {
		it("should delete the component in a transaction", () => {
			const { removeComponentsSubtree } = useComponentActions(
				mockCore.core,
				wfbm,
			);

			const openMutationTransaction = vi.spyOn(
				wfbm,
				"openMutationTransaction",
			);

			removeComponentsSubtree("1", "2");

			expect(mockCore.core.sendComponentUpdate).toHaveBeenCalledOnce();
			expect(openMutationTransaction).toHaveBeenNthCalledWith(
				1,
				"delete-1,2",
				"Delete",
			);
		});

		it("should recreate an empty page when removing all pages", () => {
			const { removeComponentsSubtree } = useComponentActions(
				mockCore.core,
				wfbm,
			);
			removeComponentsSubtree("pageId");

			expect(mockCore.core.getComponents("root")).toHaveLength(1);
		});

		it("should recreate an empty page when removing all pages", () => {
			const { removeComponentsSubtree } = useComponentActions(
				mockCore.core,
				wfbm,
			);
			removeComponentsSubtree("blueprints_blueprint-id");

			expect(mockCore.core.getComponents("blueprints_root")).toHaveLength(
				1,
			);
		});
	});

	describe("components movements", () => {
		it("should go to the parent", () => {
			const { isGoToParentAllowed, goToParent } = useComponentActions(
				mockCore.core,
				wfbm,
			);
			expect(isGoToParentAllowed("root")).toBe(false);
			expect(isGoToParentAllowed("1")).toBe(true);
			expect(isGoToParentAllowed("1.1")).toBe(true);

			goToParent("1.1");
			expect(wfbm.firstSelectedId.value).toBe("1");
		});

		it("should go to the child", () => {
			const { isGoToChildAllowed, goToChild } = useComponentActions(
				mockCore.core,
				wfbm,
			);
			expect(isGoToChildAllowed("root")).toBe(true);
			expect(isGoToChildAllowed("1")).toBe(true);
			expect(isGoToChildAllowed("1.1.1")).toBe(false);

			goToChild("1");
			expect(wfbm.firstSelectedId.value).toBe("1.1");
		});

		it("should go to the previous sibling", () => {
			const { isGoToPrevSiblingAllowed, goToPrevSibling } =
				useComponentActions(mockCore.core, wfbm);
			expect(isGoToPrevSiblingAllowed("root")).toBe(false);
			expect(isGoToPrevSiblingAllowed("1")).toBe(false);
			expect(isGoToPrevSiblingAllowed("1.1")).toBe(false);
			expect(isGoToPrevSiblingAllowed("1.2")).toBe(true);

			goToPrevSibling("1.2");
			expect(wfbm.firstSelectedId.value).toBe("1.1");
		});

		it("should go to the next sibling", () => {
			const { isGoToNextSiblingAllowed, goToNextSibling } =
				useComponentActions(mockCore.core, wfbm);
			expect(isGoToNextSiblingAllowed("root")).toBe(false);
			expect(isGoToNextSiblingAllowed("1")).toBe(true);
			expect(isGoToNextSiblingAllowed("1.1")).toBe(true);
			expect(isGoToNextSiblingAllowed("1.2")).toBe(false);

			goToNextSibling("1.1");
			expect(wfbm.firstSelectedId.value).toBe("1.2");

			goToNextSibling("1");
			expect(wfbm.firstSelectedId.value).toBe("2");
		});
	});

	describe("createAndInsertComponentsTree", () => {
		it("should create the tree in a single transaction", () => {
			const { createAndInsertComponentsTree, undo } = useComponentActions(
				mockCore.core,
				wfbm,
			);

			const [pageId, buttonId] = createAndInsertComponentsTree("root", [
				{ type: "page" },
				{
					type: "button",
					initProperties: {
						content: { text: "bar" },
					},
				},
			]);

			expect(mockCore.core.getComponents(pageId)).toHaveLength(1);
			const button = mockCore.core.getComponentById(buttonId);
			expect(button).not.toBeUndefined();
			expect(button.content.text).toStrictEqual("bar");

			undo();

			expect(mockCore.core.getComponents(pageId)).toHaveLength(0);
			expect(mockCore.core.getComponentById(pageId)).toBeUndefined();
			expect(mockCore.core.getComponentById(buttonId)).toBeUndefined();
		});
	});
});
