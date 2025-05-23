import { beforeEach, describe, expect, it, Mock, vi, vitest } from "vitest";
import { useNotesManager } from "./useNotesManager";
import { buildMockComponent, buildMockCore } from "@/tests/mocks";
import { generateBuilderManager } from "@/builder/builderManager";
import { fetchWriterApiCurrentUserProfile } from "@/composables/useWriterApiUser";

const fetchApplicationDeployment = vi.fn();
const publishApplication = vi.fn();
const fetchUserProfile = vi.fn();
const analyticsIdentify = vi.fn();

vitest.mock("@/writerApi", () => ({
	WriterApi: class {
		fetchApplicationDeployment = fetchApplicationDeployment;
		publishApplication = publishApplication;
		fetchUserProfile = fetchUserProfile;
		analyticsIdentify = analyticsIdentify;
	},
}));

vitest.mock("@/composables/useWriterApiUser", () => ({
	fetchWriterApiCurrentUserProfile: vi.fn().mockResolvedValue({ id: 1 }),
}));

describe(useNotesManager.name, () => {
	let mockCore: ReturnType<typeof buildMockCore>;
	let wfbm: ReturnType<typeof generateBuilderManager>;

	beforeEach(() => {
		mockCore = buildMockCore();
		wfbm = generateBuilderManager();
		mockCore.core.addComponent(
			buildMockComponent({ id: "p1", type: "page", parentId: "root" }),
		);
	});

	it("should create a note", async () => {
		const noteManager = useNotesManager(mockCore.core, wfbm);

		await noteManager.createNote("p1", { x: 0, y: 0 });

		expect(fetchWriterApiCurrentUserProfile).toHaveBeenCalled();

		const notes = Array.from(noteManager.getNotes("p1"));
		expect(notes).toHaveLength(1);

		expect(notes[0]).toStrictEqual(
			expect.objectContaining({
				content: {
					content: "",
					createdAt: expect.any(String),
					createdBy: "1",
					parentInstancePath: undefined,
				},
				type: "note",
				x: 0,
				y: 0,
			}),
		);
	});

	it("should delete a note", async () => {
		const noteManager = useNotesManager(mockCore.core, wfbm);

		const noteId = await noteManager.createNote("p1", { x: 0, y: 0 });
		noteManager.selectNote(noteId);

		await noteManager.deleteNote(noteId);

		expect(fetchWriterApiCurrentUserProfile).toHaveBeenCalled();
		expect(Array.from(noteManager.getNotes("p1"))).toHaveLength(0);
		expect(noteManager.selectedNoteId.value).toBeUndefined();
	});

	it("should not delete a note from other user", async () => {
		(fetchWriterApiCurrentUserProfile as Mock).mockResolvedValue({ id: 2 });

		const noteManager = useNotesManager(mockCore.core, wfbm);

		const noteId = await noteManager.createNote("p1", { x: 0, y: 0 });

		(fetchWriterApiCurrentUserProfile as Mock).mockResolvedValue({ id: 1 });

		await noteManager.deleteNote(noteId);

		expect(fetchWriterApiCurrentUserProfile).toHaveBeenCalled();
		expect(Array.from(noteManager.getNotes("p1"))).toHaveLength(1);
		expect(noteManager.selectedNoteId.value).toBe(noteId);
	});

	it("should search through notes", async () => {
		const noteManager = useNotesManager(mockCore.core, wfbm);

		mockCore.core.addComponent(
			buildMockComponent({
				id: "1",
				type: "note",
				content: {
					content: "Foo",
				},
			}),
		);
		mockCore.core.addComponent(
			buildMockComponent({
				id: "2",
				type: "note",
				content: {
					content: "Bar",
				},
			}),
		);

		expect(Array.from(noteManager.searchNotes("F"))).toHaveLength(1);
	});

	it("should get note information", async () => {
		const noteManager = useNotesManager(mockCore.core, wfbm);

		const fields = {
			content: "Foo",
			createdAt: "2025-05-23T17:30:30",
			createdBy: "1",
		};

		mockCore.core.addComponent(
			buildMockComponent({
				id: "1",
				type: "note",
				parentId: "blueprints_root",
				content: fields,
			}),
		);

		const note = mockCore.core.getComponentById("1");

		const { content, createdBy, type, state, createdAt } =
			noteManager.useNoteInformation(note);

		expect(createdBy.value).toBe(Number(fields.createdBy));
		expect(content.value).toBe(fields.content);
		expect(type.value).toBe("blueprints");
		expect(state.value).toBe("default");
		expect(createdAt.value).toBe(fields.createdAt);
	});
});
