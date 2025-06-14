import type { useWriterTracking } from "@/composables/useWriterTracking";
import { getContainableTypes } from "../core/typeHierarchy";
import { Core, BuilderManager, Component, ComponentMap } from "@/writerTypes";
import { useComponentClipboard } from "./useComponentClipboard";
import { COMPONENT_TYPES_ROOT } from "@/constants/component";

export function useComponentActions(
	wf: Core,
	ssbm: BuilderManager,
	tracking?: ReturnType<typeof useWriterTracking>,
) {
	const componentClipboard = useComponentClipboard();

	function generateNewComponentId() {
		const radix = 36;
		let newId = "";

		const randomArr = new Uint16Array(16);
		window.crypto.getRandomValues(randomArr);

		randomArr.forEach((n) => {
			newId += (n % radix).toString(radix);
		});

		return newId;
	}

	/**
	 * Moves a component up within its current container.
	 * Mutates the component and its previous sibling.
	 */
	function moveComponentUp(componentId: Component["id"]): void {
		const component = wf.getComponentById(componentId);
		if (!component) return;
		const position = component.position;
		if (position == 0) return;
		const parent = wf.getComponentById(component.parentId);
		if (!parent) return;

		const previousSibling = findSibling(componentId, -1);

		// MUTATIONS

		const transactionId = `move-up-${componentId}`;
		ssbm.openMutationTransaction(transactionId, `Move up`);

		ssbm.registerPreMutation(previousSibling);
		previousSibling.position++;
		ssbm.registerPostMutation(previousSibling);

		ssbm.registerPreMutation(component);
		component.position--;
		ssbm.registerPostMutation(component);
		ssbm.closeMutationTransaction(transactionId);
		wf.sendComponentUpdate();
	}

	/**
	 * Moves a component down within its existing container.
	 * Mutates the component and its next sibling.
	 */
	function moveComponentDown(componentId: Component["id"]): void {
		const component = wf.getComponentById(componentId);
		if (!component) return;
		const parent = wf.getComponentById(component.parentId);
		if (!parent) return;
		const position = component.position;
		if (position == -2) return; // Positionless

		const nextSibling = findSibling(componentId, 1);
		if (!nextSibling) return;

		const transactionId = `move-down-${componentId}`;
		ssbm.openMutationTransaction(transactionId, `Move down`);
		ssbm.registerPreMutation(nextSibling);
		nextSibling.position--;
		ssbm.registerPostMutation(nextSibling);
		ssbm.registerPreMutation(component);
		component.position++;
		ssbm.registerPostMutation(component);
		ssbm.closeMutationTransaction(transactionId);
		wf.sendComponentUpdate();
	}

	/**
	 * Moves a component to a different container
	 *
	 * @param componentId Id of the target component
	 * @param newParentId Id of the new parent component
	 * @param newPosition Position of the component within the new parent
	 * @returns
	 */
	function moveComponent(
		componentId: Component["id"],
		newParentId: Component["id"],
		newPosition?: number,
	) {
		const component = wf.getComponentById(componentId);
		if (!component) return;
		const currentParentComponent = wf.getComponentById(component.parentId);
		if (!currentParentComponent) return;
		if (componentId == newParentId) return;
		if (currentParentComponent.id == newParentId && newPosition === null)
			return;
		const transactionId = `move-${componentId}`;
		ssbm.openMutationTransaction(transactionId, `Move`);
		ssbm.registerPreMutation(component);
		repositionHigherSiblings(componentId, -1);
		component.position =
			newPosition ??
			getNextInsertionPosition(newParentId, component.type);
		component.parentId = newParentId;
		repositionHigherSiblings(componentId, 1);
		ssbm.registerPostMutation(component);
		ssbm.closeMutationTransaction(transactionId);
		wf.sendComponentUpdate();
	}

	function isParentSuitable(
		targetId: Component["id"],
		child: Component,
	): boolean {
		const targetComponent = wf.getComponentById(targetId);
		if (!targetComponent) return false;
		const containableTypes = wf.getContainableTypes(targetId);
		return (
			!targetComponent?.isCodeManaged &&
			!wf.isChildOf(child.id, targetId) &&
			containableTypes.includes(child.type)
		);
	}

	/**
	 * Moves a component inside the next sibling (if possible)
	 * @returns the new parent ID of the component
	 */
	function moveComponentInsideNextSibling(
		componentId: Component["id"],
	): Component["id"] | undefined {
		const component = wf.getComponentById(componentId);
		const target = findSibling(componentId, 1);
		if (!target) return;
		if (!isParentSuitable(target.id, component)) return;
		moveComponent(componentId, target.id);
		return target.id;
	}

	/**
	 * Moves a component inside the parent of the container
	 * @returns the new parent ID of the component
	 */
	function moveComponentToParent(
		componentId: Component["id"],
	): Component["id"] | undefined {
		const component = wf.getComponentById(componentId);
		const targetId = wf.getComponentById(component.parentId).parentId;
		if (!targetId) return;
		if (!isParentSuitable(targetId, component)) return;
		moveComponent(componentId, targetId, 0);
		return targetId;
	}

	function createComponent(
		type: string,
		parentId: Component["id"],
		position?: number,
		initProperties?: Partial<
			Omit<Component, "id" | "type" | "parent" | "handlers" | "position">
		>,
	) {
		const newId = generateNewComponentId();
		const definition = wf.getComponentDefinition(type);
		const { fields } = definition;
		const initContent = {};
		Object.entries(fields ?? {}).map(([fieldKey, field]) => {
			initContent[fieldKey] =
				initProperties?.["content"]?.[fieldKey] ?? field.init;
		});

		const component = {
			...(initProperties ?? {}),
			id: newId,
			type,
			parentId,
			content: initContent,
			handlers: {},
			position: position ?? getNextInsertionPosition(parentId, type),
		};

		return component;
	}

	/**
	 * Creates a component of the given type and inserts it.
	 *
	 * @param type Type of the component to be created
	 * @param parentId Id of the existing component that will contain the new component
	 * @param position Position within the parent component
	 * @returns Id of the newly created component
	 */
	function createAndInsertComponent(
		type: string,
		parentId: Component["id"],
		position?: number,
		initProperties?: Partial<
			Omit<Component, "type" | "parent" | "handlers" | "position">
		>,
		initializer?: (parentId: Component["id"]) => void,
	): Component["id"] {
		const component = createComponent(
			type,
			parentId,
			position,
			initProperties,
		);
		component.id = initProperties?.id ?? component.id;
		const transactionId = `create-${component.id}`;
		ssbm.openMutationTransaction(transactionId, `Create`);
		wf.addComponent(component);
		repositionHigherSiblings(component.id, 1);
		initializer?.(component.id);
		ssbm.registerPostMutation(component);
		ssbm.closeMutationTransaction(transactionId);
		wf.sendComponentUpdate();

		tracking?.track(
			type.startsWith("blueprints_")
				? "blueprints_block_added"
				: "ui_block_added",
			{ componentId: component.id },
		);
		return component.id;
	}

	/**
	 * Moves target component's higher siblings, which are components that share the same
	 * parent and have a higher position than the target component.
	 *
	 * @param componentId Id of the target component
	 * @param delta How many position units to add to higher siblings
	 */
	function repositionHigherSiblings(
		componentId: Component["id"],
		delta: number,
	) {
		const component = wf.getComponentById(componentId);
		const positionless = wf.getComponentDefinition(
			component.type,
		).positionless;
		if (positionless) return;
		const siblings = wf
			.getComponents(component.parentId, {
				includeBMC: true,
				includeCMC: false,
			})
			.filter((c) => c.id !== componentId);
		const higherSiblings = siblings.filter(
			(siblingComponent) =>
				siblingComponent.position >= component.position,
		);
		higherSiblings.map((c) => {
			ssbm.registerPreMutation(c);
			c.position += delta;
			ssbm.registerPostMutation(c);
		});
	}

	/**
	 * Returns a subtree (component array where item 0 is the root) for a target
	 * component and its descendents.
	 *
	 * @param componentId Id of the target component
	 * @returns Subtree
	 */
	function getFlatComponentSubtree(
		componentId: Component["id"],
	): Component[] {
		const component = wf.getComponentById(componentId);
		const subtree: Component[] = [];
		const pushToSubtreeRecursively = (rootComponent: Component) => {
			const children = wf.getComponents(rootComponent.id);
			subtree.push(rootComponent);
			children.map((child) => pushToSubtreeRecursively(child));
		};
		pushToSubtreeRecursively(component);
		return subtree;
	}

	function getNodeDependencies(componentId: Component["id"]): Component[] {
		return wf
			.getComponents()
			.filter((c) => c.outs?.find((out) => out.toNodeId == componentId));
	}

	/**
	 * Removes multiples components at the same time (including their descendents) inside an unique transaction.
	 *
	 * @param componentId Id of the target component
	 */
	function removeComponentsSubtree(...componentIds: Component["id"][]): void {
		const components = componentIds
			.map((i) => wf.getComponentById(i))
			.filter(Boolean);
		if (components.length === 0) return;

		const transactionId = `delete-${components.map((c) => c.id).join(",")}`;
		ssbm.openMutationTransaction(transactionId, `Delete`);

		for (const component of components) {
			if (component.parentId) {
				repositionHigherSiblings(component.id, -1);
			}
			const dependencies = getNodeDependencies(component.id);
			for (const c of dependencies) {
				ssbm.registerPreMutation(c);
				c.outs = [
					...c.outs.filter((out) => out.toNodeId !== component.id),
				];
			}
			tracking?.track(
				component.type.startsWith("blueprints_")
					? "blueprints_block_deleted"
					: "ui_block_deleted",
				{ componentId: component.id },
			);
			const subtree = getFlatComponentSubtree(component.id);
			for (const c of subtree) {
				ssbm.registerPreMutation(c);
				wf.deleteComponent(c.id);
				ssbm.removeSelectedComponentId(c.id);
			}
		}

		ssbm.closeMutationTransaction(transactionId);
		wf.sendComponentUpdate();
	}

	/**
	 * Removes a component and all its descendents
	 *
	 * @param componentId Id of the target component
	 */
	function removeComponentSubtree(componentId: Component["id"]): void {
		return removeComponentsSubtree(componentId);
	}

	/**
	 * Whether a target component is the root
	 */
	function isRoot(targetId: Component["id"]): boolean {
		return COMPONENT_TYPES_ROOT.has(targetId);
	}

	/**
	 * Whether a component can be dragged.
	 */
	function isDraggingAllowed(targetId: Component["id"]): boolean {
		const component = wf.getComponentById(targetId);
		return !isRoot(targetId) && !component?.isCodeManaged;
	}

	/**
	 * Whether a component can be added to the target component.
	 */
	function isAddAllowed(targetId: Component["id"]): boolean {
		const component = wf.getComponentById(targetId);
		return (
			!component?.isCodeManaged &&
			wf.getContainableTypes(targetId).length > 0
		);
	}

	/**
	 * Whether a component can be copied into the clipboard.
	 */
	function isCopyAllowed(targetId: Component["id"]): boolean {
		return !isRoot(targetId);
	}

	/**
	 * Whether a component can be cut and placed in the clipboard.
	 */
	function isCutAllowed(targetId: Component["id"]): boolean {
		const component = wf.getComponentById(targetId);
		return !isRoot(targetId) && !component?.isCodeManaged;
	}

	/**
	 * Whether a component can be deleted.
	 */
	function isDeleteAllowed(targetId: Component["id"]): boolean {
		const component = wf.getComponentById(targetId);
		return !isRoot(targetId) && !component?.isCodeManaged;
	}

	/** Whether it's possible to go to (select) a component's parent. */
	function isGoToParentAllowed(targetId: Component["id"]): boolean {
		return !isRoot(targetId);
	}
	/** Whether it's possible to go to (select) a component's children. */
	function isGoToChildAllowed(targetId: Component["id"]): boolean {
		return wf.getComponents(targetId).length > 0;
	}
	/** Whether it's possible to go to (select) the next component sibling. */
	function isGoToNextSiblingAllowed(targetId: Component["id"]): boolean {
		return Boolean(findSibling(targetId, 1));
	}
	/** Whether it's possible to go to (select) the previous component sibling. */
	function isGoToPrevSiblingAllowed(targetId: Component["id"]): boolean {
		return Boolean(findSibling(targetId, -1));
	}

	/**
	 * Go to (select) a target component's parent.
	 *
	 * @param targetId Id of the target component
	 * @param targetInstancePath Flattened instance path of a specific component instance
	 */
	function goToParent(
		targetId: Component["id"],
		targetInstancePath?: string,
	) {
		const targetComponent = wf.getComponentById(targetId);
		if (!targetComponent) return;
		const parentId = targetComponent.parentId;
		if (!parentId) return;

		let parentInstancePath: string;
		if (targetInstancePath) {
			parentInstancePath = targetInstancePath
				.split(",")
				.slice(0, -1)
				.join(",");
		}
		ssbm.setSelection(parentId, parentInstancePath);
	}

	/**
	 * Go to (select) a target component's parent.
	 *
	 * @param targetId Id of the target component
	 * @param targetInstancePath Flattened instance path of a specific component instance
	 */
	function goToChild(targetId: Component["id"]) {
		const child = wf
			.getComponents(targetId)
			.sort((a, b) => a.position - b.position)
			.at(0);
		if (child) ssbm.setSelection(child.id);
	}

	function findSibling(targetId: Component["id"], direction: -1 | 1) {
		if (isRoot(targetId)) return;
		const target = wf.getComponentById(targetId);
		if (!target) return;
		const { parentId, position } = target;

		const targetPosition = position + direction;

		return wf
			.getComponents(parentId, { includeBMC: true, includeCMC: false })
			.find(
				(c) => c.position === targetPosition && c.parentId === parentId,
			);
	}
	/** Whether it's possible to go to (select) the next component sibling. */
	function goToNextSibling(targetId: Component["id"]) {
		if (isRoot(targetId)) return;
		const parentId = wf.getComponentById(targetId)?.parentId;
		if (!parentId) return;
		const siblings = wf
			.getComponents(parentId)
			.sort((a, b) => a.position - b.position);
		const index = siblings.findIndex((c) => c.id === targetId);
		if (index === -1 && index + 1 === siblings.length) return;
		ssbm.setSelection(siblings[index + 1]?.id);
	}
	/** Whether it's possible to go to (select) the previous component sibling. */
	function goToPrevSibling(targetId: Component["id"]) {
		const sibling = findSibling(targetId, -1);
		if (sibling) ssbm.setSelection(sibling.id);
	}

	/**
	 * Returns whether the components in a subtree can be incorporated
	 * to the system.
	 */
	function isSubtreeIngestable(subtree: Component[]) {
		/**
		 * This is a non-trivial operation given the complexity
		 * created by inheritance mechanisms in component parenting.
		 *
		 * For example, a Repeater with a nested Repeater with a Column
		 * can only be pasted in a Column Container. But a Repeater with a Section
		 * can be pasted almost anywhere.
		 */

		if (subtree.length == 0) return false;

		/*
		A component map is created by combining existing elements
		with the tentative elements in the subtree.
		*/

		const componentMap: ComponentMap = {};
		[...wf.getComponents(), ...subtree].forEach((component) => {
			componentMap[component.id] = component;
		});

		const isViable = subtree
			.map((component) => {
				const containableTypes = getContainableTypes(
					componentMap,
					component.parentId,
				);
				return containableTypes.includes(component.type);
			})
			.every((item) => item);
		return isViable;
	}

	/**
	 * Returns whether the current contents of the internal clipboard can be
	 * pasted to the target component.
	 */
	function isPasteAllowed(targetId: Component["id"]): boolean {
		const component = wf.getComponentById(targetId);
		if (!component || component.isCodeManaged) return false;
		return true;
	}

	/**
	 * Returns whether the component can be moved up, and whether it can
	 * be moved down.
	 *
	 * @param targetId Id of the target Component
	 */
	function getEnabledMoves(targetId: Component["id"]) {
		const getPositionableChildrenCount = (parentId: Component["id"]) => {
			const children = wf.getComponents(parentId, {
				includeBMC: true,
				includeCMC: false,
			});
			const positionableChildren = children.filter((c) => {
				const positionless = wf.getComponentDefinition(
					c.type,
				)?.positionless;
				if (positionless) return false;
				return true;
			});
			return positionableChildren.length;
		};

		const component = wf.getComponentById(targetId);
		if (!component || component.isCodeManaged) {
			return { up: false, down: false };
		}
		const definition = wf.getComponentDefinition(component.type);
		if (definition.positionless) return { up: false, down: false };
		const positionableSiblingCount = component.parentId
			? getPositionableChildrenCount(component.parentId)
			: 0;
		const isUpEnabled =
			positionableSiblingCount > 0 && component.position > 0;
		const isDownEnabled =
			positionableSiblingCount > 0 &&
			component.position < positionableSiblingCount - 1;
		return { up: isUpEnabled, down: isDownEnabled };
	}

	/**
	 * Cuts a component and its descendents and places them in the internal clipboard.
	 * @param componentId Id of the component to be cut
	 */
	function cutComponent(componentId: Component["id"]): void {
		const component = wf.getComponentById(componentId);
		if (!component) return;
		const components = getFlatComponentSubtree(componentId);
		componentClipboard.set(components);
		ssbm.setSelection(null);
		removeComponentSubtree(componentId);
		wf.sendComponentUpdate();
	}

	/**
	 * Returns a deep copy of the given subtree with all its component IDs
	 * regenerated.
	 */
	function getNewSubtreeWithRegeneratedIds(subtree: Component[]) {
		const deepCopiedSubtree: Component[] = JSON.parse(
			JSON.stringify(subtree),
		);
		deepCopiedSubtree.forEach((c) => {
			delete c.isCodeManaged;
			const newId = generateNewComponentId();
			deepCopiedSubtree
				.filter((nc) => nc.id !== c.id)
				.map((nc) => {
					if (nc.parentId == c.id) {
						nc.parentId = newId;
					}
					nc.outs?.forEach((out) => {
						if (out.toNodeId == c.id) {
							out.toNodeId = newId;
						}
					});
				});
			c.id = newId;
			if (typeof c.x !== "undefined" && typeof c.y !== "undefined") {
				c.x += 36;
				c.y += 36;
			}
		});
		return deepCopiedSubtree;
	}

	/**
	 * Copies a component and its descendents into the clipboard
	 * @param componentId Id of the component to be copied
	 * @returns
	 */
	function copyComponent(componentId: Component["id"]): void {
		const component = wf.getComponentById(componentId);
		if (!component) return;
		const subtree = getFlatComponentSubtree(componentId);
		const newSubtree = getNewSubtreeWithRegeneratedIds(subtree);
		componentClipboard.set(newSubtree);
	}

	/**
	 * Pastes the contents of the clipboard into a given component
	 * @param targetParentId Id of the component where to paste the clipboard
	 */
	async function pasteComponent(targetParentId: Component["id"]) {
		const targetParent = wf.getComponentById(targetParentId);
		if (!targetParent) return;

		const subtree = await componentClipboard.get();

		if (!subtree) throw Error("The clipboard doesn't contain Writer data");
		if (!subtree.length)
			throw Error("The clipboard doesn't contain components");

		const rootComponent = subtree[0];
		if (
			typeof rootComponent.outs !== "undefined" &&
			rootComponent.parentId !== targetParentId
		) {
			rootComponent.outs = [];
		}

		return pasteCopyComponent(targetParentId, subtree);
	}

	/**
	 * Pastes a subtree that has been obtained via a copy operation.
	 */
	function pasteCopyComponent(
		targetParentId: Component["id"],
		subtree: Component[],
	) {
		componentClipboard.set(getNewSubtreeWithRegeneratedIds(subtree));

		// MUTATION

		const rootComponent = subtree[0];
		rootComponent.parentId = targetParentId;
		rootComponent.position = getNextInsertionPosition(
			targetParentId,
			rootComponent.type,
		);

		if (!isSubtreeIngestable(subtree)) {
			throw Error("Could not paste the components here");
		}

		const transactionId = `paste-copy-${targetParentId}`;
		ssbm.openMutationTransaction(transactionId, `Paste from copy`);
		subtree.map((c) => {
			wf.addComponent(c);
			ssbm.registerPostMutation(c);
		});
		ssbm.closeMutationTransaction(transactionId);
		wf.sendComponentUpdate();
	}

	/**
	 * Returns the default position for the next insertion into the given component.
	 */
	function getNextInsertionPosition(
		targetParentId: Component["id"],
		childType: Component["type"],
	) {
		const positionless = wf.getComponentDefinition(childType).positionless;
		if (positionless) {
			return -2;
		}

		const positionfulChildren = wf
			.getComponents(targetParentId, {
				includeBMC: true,
				includeCMC: false,
			})
			.filter((c) => c.position !== -2);

		if (positionfulChildren.length > 0) {
			const position = Math.max(
				Math.max(
					...positionfulChildren.map((c: Component) => c.position),
				) + 1,
				0,
			);
			return position;
		} else {
			return 0;
		}
	}

	/**
	 * Get a snapshot of the current state of mutations transactions:
	 * - Whether Undo and Redo transactions are available
	 * - A short description of Undo and Redo transactions
	 */
	function getUndoRedoSnapshot() {
		const snapshot = ssbm.getMutationTransactionsSnapshot();
		return {
			isUndoAvailable: !!snapshot.undo,
			isRedoAvailable: !!snapshot.redo,
			undoDesc: snapshot.undo?.desc,
			redoDesc: snapshot.redo?.desc,
		};
	}

	/**
	 * Undo mutation transaction.
	 */
	function undo() {
		const transaction = ssbm.consumeUndoTransaction();
		if (!transaction) return;

		Object.entries(transaction.mutations).forEach(
			([mutationId, mutation]) => {
				if (mutation.jsonPre && mutation.jsonPost) {
					wf.addComponent(JSON.parse(mutation.jsonPre));
					return;
				}

				if (!mutation.jsonPre && mutation.jsonPost) {
					wf.deleteComponent(mutationId);
					return;
				}

				if (mutation.jsonPre && !mutation.jsonPost) {
					wf.addComponent(JSON.parse(mutation.jsonPre));
					return;
				}
			},
		);
		wf.sendComponentUpdate();
	}

	/**
	 * Redo previously undone mutation transaction.
	 */
	function redo() {
		const transaction = ssbm.consumeRedoTransaction();
		if (!transaction) return;

		Object.entries(transaction.mutations).forEach(
			([mutationId, mutation]) => {
				if (mutation.jsonPre && mutation.jsonPost) {
					wf.addComponent(JSON.parse(mutation.jsonPost));
					return;
				}

				if (!mutation.jsonPre && mutation.jsonPost) {
					wf.addComponent(JSON.parse(mutation.jsonPost));
					return;
				}

				if (mutation.jsonPre && !mutation.jsonPost) {
					wf.deleteComponent(mutationId);
					return;
				}
			},
		);
		wf.sendComponentUpdate();
	}

	/**
	 * Set a value for a component content field
	 */
	function setContentValue(
		componentId: Component["id"],
		fieldKey: string,
		value: string,
	) {
		const component = wf.getComponentById(componentId);
		if (!component) return;
		const transactionId = `edit-${componentId}-content-${fieldKey}`;
		ssbm.openMutationTransaction(transactionId, `Edit property`, true);
		ssbm.registerPreMutation(component);

		component.content[fieldKey] = value;

		ssbm.registerPostMutation(component);
		ssbm.closeMutationTransaction(transactionId);
		wf.sendComponentUpdate();
	}

	/**
	 * Add an out
	 */
	function addOut(
		componentId: Component["id"],
		out: Component["outs"][number],
	) {
		const component = wf.getComponentById(componentId);
		if (!component) return;
		const transactionId = `add-${componentId}-out-${out.outId}-${out.toNodeId}`;
		ssbm.openMutationTransaction(transactionId, `Add out`, true);
		ssbm.registerPreMutation(component);

		component.outs = [...(component.outs ?? []), out];

		ssbm.registerPostMutation(component);
		ssbm.closeMutationTransaction(transactionId);
		wf.sendComponentUpdate();
		tracking?.track("ui_blueprint_connected", {
			componentIds: [componentId, out.toNodeId],
			outId: out.outId,
		});
	}

	/**
	 * Remove an out
	 */
	function removeOut(
		componentId: Component["id"],
		out: Component["outs"][number],
	) {
		const component = wf.getComponentById(componentId);
		if (!component) return;
		const transactionId = `edit-${componentId}-out-${out.outId}-${out.toNodeId}`;
		ssbm.openMutationTransaction(transactionId, "Edit out", true);
		ssbm.registerPreMutation(component);

		component.outs = component.outs.filter(
			(o) => !(out.outId === o.outId && out.toNodeId === o.toNodeId),
		);

		ssbm.registerPostMutation(component);
		ssbm.closeMutationTransaction(transactionId);
		wf.sendComponentUpdate();
	}

	/**
	 * Change coordinates
	 */
	function changeCoordinates(
		componentId: Component["id"],
		x: number,
		y: number,
	) {
		const component = wf.getComponentById(componentId);
		if (!component) return;

		const transactionId = `change-${componentId}-coordinates`;
		ssbm.openMutationTransaction(
			transactionId,
			"Change coordinates",
			false,
		);
		ssbm.registerPreMutation(component);

		component.x = Math.floor(x);
		component.y = Math.floor(y);

		ssbm.registerPostMutation(component);
		ssbm.closeMutationTransaction(transactionId);
		wf.sendComponentUpdate();
	}

	/***
	 * Change the coordinates of multiple components.
	 */
	function changeCoordinatesMultiple(
		coordinates: Record<Component["id"], { x: number; y: number }>,
	) {
		const entries = Object.entries(coordinates);
		if (entries.length == 0) return;

		const transactionId = `change-multiple-coordinates-${Object.keys(coordinates).join(",")}`;
		ssbm.openMutationTransaction(
			transactionId,
			"Change coordinates",
			false,
		);

		entries.forEach(([componentId, { x, y }]) => {
			const component = wf.getComponentById(componentId);
			if (!component) return;
			ssbm.registerPreMutation(component);
			component.x = Math.floor(x);
			component.y = Math.floor(y);
			ssbm.registerPostMutation(component);
		});

		ssbm.closeMutationTransaction(transactionId);
		wf.sendComponentUpdate();
	}

	/**
	 * Set the value for a component's visibility.
	 */
	function setVisibleValue(
		componentId: Component["id"],
		visible: boolean | string,
		binding: string = "",
		reversed: boolean = false,
	) {
		const component = wf.getComponentById(componentId);
		if (!component) return;
		const transactionId = `change-visibility-${componentId}`;
		ssbm.openMutationTransaction(transactionId, `Change visibility`, true);
		ssbm.registerPreMutation(component);

		if (component.visible == null) {
			component.visible = {
				expression: true,
				binding: "",
				reversed: false,
			};
		}

		if (typeof visible == "boolean") {
			component.visible.expression = visible;
		} else if (visible == "custom") {
			component.visible = {
				expression: "custom",
				binding: binding,
				reversed: reversed,
			};
		}

		ssbm.registerPostMutation(component);
		ssbm.closeMutationTransaction(transactionId);
		wf.sendComponentUpdate();
	}

	/**
	 * Set a component's two-way binding.
	 */
	function setBinding(
		componentId: Component["id"],
		stateRef: Component["binding"]["stateRef"],
		targetEventType?: Component["binding"]["eventType"],
	) {
		const component = wf.getComponentById(componentId);
		if (!component) return;

		let eventType: string;
		if (targetEventType) {
			eventType = targetEventType;
		} else {
			const definition = wf.getComponentDefinition(component.type);
			const events = Object.entries(definition.events).filter(
				([eventType, event]) => event.bindable,
			);
			const bindableEventTypes = events.map(
				([eventType, event]) => eventType,
			);
			eventType = bindableEventTypes?.[0];
		}

		if (!eventType) return;

		const transactionId = `change-binding-${componentId}`;
		ssbm.openMutationTransaction(transactionId, `Change binding`, true);
		ssbm.registerPreMutation(component);

		if (stateRef) {
			component.binding = {
				eventType,
				stateRef,
			};
		} else {
			delete component.binding;
		}
		ssbm.registerPostMutation(component);
		ssbm.closeMutationTransaction(transactionId);
		wf.sendComponentUpdate();
	}

	/**
	 * Set an event handler for a component.
	 */
	function setHandlerValue(
		componentId: Component["id"],
		eventType: string,
		userFunction: string,
	) {
		const component = wf.getComponentById(componentId);
		if (!component) return;
		const transactionId = `set-handler-${componentId}`;
		ssbm.openMutationTransaction(transactionId, `Set event handler`, true);
		ssbm.registerPreMutation(component);

		if (userFunction) {
			if (!component.handlers) {
				component.handlers = {};
			}
			component.handlers[eventType] = userFunction;
		} else {
			delete component.handlers[eventType];
			if (Object.keys(component.handlers).length == 0) {
				delete component.handlers;
			}
		}

		ssbm.registerPostMutation(component);
		ssbm.closeMutationTransaction(transactionId);
		wf.sendComponentUpdate();
	}

	function getContainingPageId(
		componentId: Component["id"],
	): Component["id"] {
		const component = wf.getComponentById(componentId);
		if (!component || component.type == "root") return null;
		if (
			component.type == "page" ||
			component.type == "blueprints_blueprint"
		)
			return componentId;
		return getContainingPageId(component.parentId);
	}

	async function goToComponentParentPage(componentId: Component["id"]) {
		const component = wf.getComponentById(componentId);
		if (!component) return;
		const componentDefinition = wf.getComponentDefinition(
			component.type,
		)?.name;
		if (!componentDefinition) return; // Unknown component, not rendered
		wf.setActivePageId(getContainingPageId(componentId));
	}

	return {
		generateNewComponentId,
		moveComponent,
		moveComponentUp,
		moveComponentDown,
		cutComponent,
		copyComponent,
		pasteComponent,
		createAndInsertComponent,
		removeComponentSubtree,
		removeComponentsSubtree,
		isPasteAllowed,
		undo,
		redo,
		setContentValue,
		addOut,
		removeOut,
		changeCoordinates,
		changeCoordinatesMultiple,
		setVisibleValue,
		setBinding,
		getUndoRedoSnapshot,
		setHandlerValue,
		isAddAllowed,
		isCopyAllowed,
		isCutAllowed,
		isDeleteAllowed,
		isGoToParentAllowed,
		isGoToChildAllowed,
		isGoToNextSiblingAllowed,
		isGoToPrevSiblingAllowed,
		repositionHigherSiblings,
		isDraggingAllowed,
		getEnabledMoves,
		goToParent,
		goToChild,
		goToNextSibling,
		goToPrevSibling,
		goToComponentParentPage,
		moveComponentInsideNextSibling,
		moveComponentToParent,
	};
}
