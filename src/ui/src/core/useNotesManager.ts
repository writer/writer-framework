import type { generateCore } from "@/core";
import type { Point } from "@/utils/geometry";
import { useComponentActions } from "../builder/useComponentActions";
import { generateBuilderManager } from "../builder/builderManager";
import {
	ref,
	computed,
	unref,
	MaybeRef,
	readonly,
	shallowRef,
	watch,
} from "vue";
import { Component, InstancePath } from "@/writerTypes";
import { fetchWriterApiCurrentUserProfile } from "@/composables/useWriterApiUser";
import { useToasts } from "../builder/useToast";
import { flattenInstancePath } from "@/renderer/instancePath";

export type NoteState = "default" | "hover" | "active" | "new" | "cursor";
export type NoteSelectionMode = "show" | "edit";
export interface ComponentNote extends Component {
	content: Record<
		"parentInstancePath" | "content" | "createdBy" | "createdAt",
		string
	>;
}
export type ComponentNoteDraft = Pick<
	ComponentNote,
	"id" | "content" | "x" | "y" | "parentId" | "type"
>;

export function useNotesManager(
	wf: ReturnType<typeof generateCore>,
	wfbm: ReturnType<typeof generateBuilderManager>,
) {
	const toasts = useToasts();

	const { removeComponentSubtree, generateNewComponentId } =
		useComponentActions(wf, wfbm);

	const isAnnotating = ref(false);
	const selectedNoteId = ref<Component["id"] | undefined>();
	const selectedNoteMode = ref<NoteSelectionMode>("show");
	const hoveredNoteId = ref<Component["id"] | undefined>();

	const noteDraft = shallowRef<ComponentNoteDraft | undefined>();

	const selectedNote = computed<
		ComponentNote | ComponentNoteDraft | undefined
	>(() => {
		return selectedNoteId.value ? getNote(selectedNoteId.value) : undefined;
	});

	async function isOwnedByCurrentUser(
		note: ComponentNote | ComponentNoteDraft,
	) {
		const createdBy = useNoteInformation(note).createdBy.value;
		const currentUser = await fetchWriterApiCurrentUserProfile();
		return createdBy === currentUser.id;
	}

	async function selectNote(
		componentId: Component["id"] | undefined,
		mode: NoteSelectionMode = "show",
	) {
		if (componentId === undefined) {
			noteDraft.value = undefined;
			selectedNoteId.value = undefined;
			selectedNoteMode.value = "show";
			return;
		}

		if (mode === "edit") {
			const note = getNote(componentId);
			if (!(await isOwnedByCurrentUser(note))) {
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

	/**
	 * Setup a temporary `noteDraft` component that is not insterted in the tree yet
	 */
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

		const profile = await fetchWriterApiCurrentUserProfile();

		const noteId = generateNewComponentId();

		noteDraft.value = {
			id: noteId,
			type: "note",
			parentId,
			content: {
				parentInstancePath,
				content: "",
				createdBy: String(profile.id),
				createdAt: new Date().toISOString(),
			},
			x: "x" in options ? options.x : undefined,
			y: "y" in options ? options.y : undefined,
		};

		await selectNote(noteId, "edit");
		return noteId;
	}

	// remove the draft if the selection change
	watch(selectedNoteId, () => {
		if (noteDraft.value && noteDraft.value.id !== selectedNoteId.value) {
			noteDraft.value = undefined;
		}
	});

	async function deleteNote(componentId: string) {
		const note = getNote(componentId);
		if (!(await isOwnedByCurrentUser(note))) {
			return toasts.pushToast({
				type: "error",
				message:
					"You cannot delete this note because it was created by another user",
			});
		}
		selectNote(undefined);
		removeComponentSubtree(componentId);
	}

	function* getAllNotes() {
		yield* getNotes("root");
		yield* getNotes("blueprints_root");
		if (noteDraft.value) yield readonly(noteDraft.value);
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

	function* getNotes(
		parentId: string,
	): Generator<ComponentNote | ComponentNoteDraft> {
		for (const component of wf.getComponentsNested(parentId)) {
			if (component.type === "note") yield component;
		}

		if (noteDraft.value) {
			let noteParentId = noteDraft.value.parentId;

			while (noteParentId) {
				if (noteParentId === parentId) {
					yield readonly(noteDraft.value);
					return;
				}
				noteParentId = wf.getComponentById(noteParentId)?.parentId;
			}
		}
	}

	function getNote(
		componentId: string,
	): ComponentNote | ComponentNoteDraft | undefined {
		const component = wf.getComponentById(componentId);
		if (component?.type === "note") return component;

		// fallback to draft note if not found
		if (noteDraft.value?.id === componentId) {
			return readonly(noteDraft.value);
		}
	}

	const getNoteContent = (
		note: Component | ComponentNote | ComponentNoteDraft,
	) => String(note.content?.content ?? "");

	function useNoteInformation(
		component: MaybeRef<Component | ComponentNote | ComponentNoteDraft>,
	) {
		const formatter = new Intl.DateTimeFormat(undefined, {
			dateStyle: "short",
			timeStyle: "short",
		});

		const state = computed<NoteState>(() => {
			const id = unref(component)?.id;
			const content = unref(component)?.content;
			if (hoveredNoteId.value === id) return "hover";

			const isActive = selectedNote.value?.id === id;
			if (isActive) {
				return content.content ? "active" : "new";
			}

			return "default";
		});

		const content = computed(() => getNoteContent(unref(component)));

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
		getNoteContent,
	};
}
