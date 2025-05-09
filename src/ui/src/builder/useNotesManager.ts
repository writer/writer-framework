import type { generateCore } from "@/core";
import type { Point } from "@/utils/geometry";
import { useComponentActions } from "./useComponentActions";
import { generateBuilderManager } from "./builderManager";
import { useLogger } from "@/composables/useLogger";

export function useNotesManager(
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

	return { createNote };
}
