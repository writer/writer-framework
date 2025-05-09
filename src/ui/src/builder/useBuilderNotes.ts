import type { generateCore } from "@/core";
import type { Point } from "@/utils/geometry";
import { useComponentActions } from "./useComponentActions";
import { generateBuilderManager } from "./builderManager";
import { useLogger } from "@/composables/useLogger";

export function useBuilderNotes(
	wf: ReturnType<typeof generateCore>,
	wfbm: ReturnType<typeof generateBuilderManager>,
) {
	const { createAndInsertComponent } = useComponentActions(wf, wfbm);
	const logger = useLogger();

	function createNote(parentId: string, coordinates: Point) {
		const component = createAndInsertComponent(
			"comment",
			parentId,
			undefined,
			{
				content: {
					createdBy: "1",
					createdAt: new Date().toISOString(),
				},
				x: coordinates.x,
				y: coordinates.y,
			},
		);
		logger.log("##useNotesManager.createNote", component);
	}

	function* getAllNotes() {
		yield* getNotes("root");
		yield* getNotes("blueprints_root");
	}

	function* getNotes(parentId: string) {
		for (const component of wf.getComponentsNested(parentId)) {
			if (component.type === "comment") yield component;
		}
	}

	return { createNote, getNotes, getAllNotes };
}
