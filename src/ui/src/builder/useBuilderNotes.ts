import type { generateCore } from "@/core";
import type { Point } from "@/utils/geometry";
import { useComponentActions } from "./useComponentActions";
import { generateBuilderManager } from "./builderManager";
import { ref, computed, unref, MaybeRef, readonly } from "vue";
import { Component, InstancePath } from "@/writerTypes";
import { useWriterApi } from "@/composables/useWriterApi";
import { useWriterApiCurrentUserProfile } from "@/composables/useWriterApiUser";
import { useToasts } from "./useToast";
import { flattenInstancePath } from "@/renderer/instancePath";

export type NoteState = "default" | "hover" | "active" | "new" | "cursor";
export type NoteSelectionMode = "show" | "edit";

export function useBuilderNotes(
	wf: ReturnType<typeof generateCore>,
	wfbm: ReturnType<typeof generateBuilderManager>,
) {
	const { writerApi } = useWriterApi();
	const toasts = useToasts();

	const getCurrentUserProfile = useWriterApiCurrentUserProfile(writerApi);

	const { createAndInsertComponent, removeComponentSubtree } =
		useComponentActions(wf, wfbm);

	const isAnnotating = ref(false);
	const selectedNoteId = ref<Component["id"] | undefined>();
	const selectedNoteMode = ref<NoteSelectionMode>("show");
	const hoveredNoteId = ref<Component["id"] | undefined>();

	const selectedNote = computed<Component | undefined>(() => {
		return selectedNoteId.value ? getNote(selectedNoteId.value) : undefined;
	});

	async function selectNote(
		componentId: Component["id"] | undefined,
		mode: NoteSelectionMode = "show",
	) {
		if (componentId === undefined) {
			selectedNoteId.value = undefined;
			selectedNoteMode.value = "show";
			return;
		}

		if (mode === "edit") {
			const note = getNote(componentId);
			const createdBy = useNoteInformation(note).createdBy.value;
			const currentUser = await getCurrentUserProfile();
			if (createdBy !== currentUser.id) {
				return toasts.pushToast({
					type: "error",
					message:
						"You cannot edit this note because it was created by another user",
				});
			}
		}
		selectedNoteMode.value = mode;
		selectedNoteId.value = componentId;

		navigateToNote(componentId);
	}

	/**
	 * Navigate to the place where the note exists (blueprint or page)
	 */
	function navigateToNote(componentId: Component["id"]) {
		let parent = wf.getComponentById(componentId);

		while (parent) {
			switch (parent.type) {
				case "blueprints_root":
					wfbm.mode.value = "blueprints";
					break;
				case "root":
					wfbm.mode.value = "ui";
					break;
				case "blueprints_blueprint":
				case "page":
					wf.setActivePageId(parent.id);
					break;
			}

			parent = wf.getComponentById(parent.parentId);
		}
	}

	async function createNote(
		parentId: Component["id"],
		options: { instancePath: InstancePath | string } | Partial<Point>,
	) {
		let parentInstancePath = undefined;
		if ("instancePath" in options) {
			parentInstancePath =
				typeof options.instancePath === "string"
					? options.instancePath
					: flattenInstancePath(options.instancePath);
		}

		const profile = await getCurrentUserProfile();
		const noteId = createAndInsertComponent("note", parentId, undefined, {
			content: {
				parentInstancePath,
				content: "",
				createdBy: String(profile.id),
				createdAt: new Date().toISOString(),
			},
			x: "x" in options ? options.x : undefined,
			y: "y" in options ? options.y : undefined,
		});
		selectNote(noteId, "edit");
	}

	function deleteNote(componentId: string) {
		selectNote(undefined);
		removeComponentSubtree(componentId);
	}

	function* getAllNotes() {
		yield* getNotes("root");
		yield* getNotes("blueprints_root");
	}

	function* searchNotes(query: string) {
		if (!query) {
			yield* getAllNotes();
			return;
		}

		const queryLocale = query.toLocaleLowerCase();

		for (const note of getAllNotes()) {
			if (!note.content.content) continue;
			const isMatching = String(note.content.content)
				.toLocaleLowerCase()
				.includes(queryLocale);
			if (isMatching) {
				yield note;
			}
		}
	}

	function* getNotes(parentId: string) {
		for (const component of wf.getComponentsNested(parentId)) {
			if (component.type === "note") yield component;
		}
	}

	function getNote(componentId: string) {
		const component = wf.getComponentById(componentId);
		if (component?.type === "note") return component;
	}

	function useNoteInformation(component: MaybeRef<Component>) {
		const formatter = new Intl.DateTimeFormat(undefined, {
			dateStyle: "short",
			timeStyle: "short",
		});

		const state = computed<NoteState>(() => {
			const { id, content } = unref(component);
			if (hoveredNoteId.value === id) return "hover";

			const isActive = selectedNote.value?.id === id;
			if (isActive) {
				return content.content ? "active" : "new";
			}

			return "default";
		});

		const content = computed(() => unref(component).content.content);

		const createdAt = computed(() => unref(component).content.createdAt);

		const parentInstancePath = computed<string | undefined>(() => {
			return unref(component).content.parentInstancePath;
		});

		const createdBy = computed(() => {
			const createdBy = unref(component).content?.createdBy;
			return createdBy ? Number(createdBy) : undefined;
		});

		const createdAtFormatted = computed(() => {
			if (!createdAt.value) return "";
			const date = new Date(createdAt.value);
			return formatter.format(date);
		});

		const type = computed<"ui" | "blueprints">(() => {
			const rootId = getComponentRoot(unref(component).id);
			return rootId === "blueprints_root" ? "blueprints" : "ui";
		});

		function getComponentRoot(componentId: string) {
			const component = wf.getComponentById(componentId);
			if (!component) return componentId;
			return getComponentRoot(component.parentId) ?? componentId;
		}

		return {
			content,
			type,
			createdBy,
			createdAt,
			createdAtFormatted,
			state,
			parentInstancePath,
		};
	}

	return {
		isAnnotating,
		createNote,
		getNotes,
		selectNote,
		searchNotes,
		getAllNotes,
		deleteNote,
		selectedNoteId: readonly(selectedNoteId),
		selectedNoteMode: readonly(selectedNoteMode),
		selectedNote,
		hoveredNoteId,
		useNoteInformation,
	};
}
