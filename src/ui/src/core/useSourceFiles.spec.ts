import { describe, expect, it, vi } from "vitest";
import { useSourceFiles } from "./useSourceFiles";
import { buildMockCore } from "@/tests/mocks";
import { flushPromises } from "@vue/test-utils";

describe(useSourceFiles.name, () => {
	it("should open a file", () => {
		const { core, sourceFiles } = buildMockCore();
		sourceFiles.value = {
			type: "directory",
			children: {
				"main.py": {
					type: "file",
					content: "print('hello')",
					complete: true,
				},
			},
		};
		const { openFile, filepathOpen, code } = useSourceFiles(core);

		openFile(["main.py"]);

		expect(filepathOpen.value).toStrictEqual(["main.py"]);
		expect(code.value).toStrictEqual("print('hello')");
	});

	it("should edit a file a compute edited file", () => {
		const { core, sourceFiles } = buildMockCore();
		sourceFiles.value = {
			type: "directory",
			children: {
				"a.txt": {
					type: "file",
					content: "A",
					complete: true,
				},
				"b.txt": {
					type: "file",
					content: "B",
					complete: true,
				},
				c: {
					type: "directory",
					children: {
						"c.txt": {
							type: "file",
							content: "C",
							complete: true,
						},
					},
				},
			},
		};
		const { openFile, code, pathsUnsaved } = useSourceFiles(core);

		openFile(["a.txt"]);
		code.value = "X";

		expect(pathsUnsaved.value).toStrictEqual([["a.txt"]]);

		openFile(["c", "c.txt"]);
		code.value = "X";

		expect(pathsUnsaved.value).toStrictEqual([["a.txt"], ["c", "c.txt"]]);
	});

	it("should add a file to the draft", async () => {
		const { core, sourceFiles } = buildMockCore();
		sourceFiles.value = { type: "directory", children: {} };

		const { sourceFileDraft } = useSourceFiles(core);
		expect(sourceFileDraft.value).toStrictEqual(sourceFiles.value);

		sourceFiles.value = {
			type: "directory",
			children: {
				"a.txt": { type: "file", content: "", complete: true },
			},
		};
		await flushPromises();
		expect(sourceFileDraft.value).toStrictEqual(sourceFiles.value);
	});

	it("should remove a file to the draft", async () => {
		const { core, sourceFiles } = buildMockCore();
		sourceFiles.value = {
			type: "directory",
			children: {
				"a.txt": { type: "file", content: "", complete: true },
			},
		};

		const { sourceFileDraft } = useSourceFiles(core);
		expect(sourceFileDraft.value).toStrictEqual(sourceFiles.value);

		sourceFiles.value = {
			type: "directory",
			children: {},
		};
		await flushPromises();
		expect(sourceFileDraft.value).toStrictEqual(sourceFiles.value);
	});

	describe("lazy loading", () => {
		it("should request fetchig whole file on opening", () => {
			const { core, sourceFiles } = buildMockCore();

			const requestSourceFileLoading = vi
				.spyOn(core, "requestSourceFileLoading")
				.mockImplementation(async () => {});

			sourceFiles.value = {
				type: "directory",
				children: {
					"a.txt": {
						type: "file",
						content: "A",
						complete: false,
					},
					"b.txt": {
						type: "file",
						content: "B",
						complete: true,
					},
				},
			};

			const { openFile } = useSourceFiles(core);

			openFile(["a.txt"]);
			expect(requestSourceFileLoading).toHaveBeenNthCalledWith(1, [
				"a.txt",
			]);

			openFile(["b.txt"]);
			expect(requestSourceFileLoading).toHaveBeenCalledOnce();
		});

		it("should refresh the draft when file is loaded", async () => {
			const { core, sourceFiles } = buildMockCore();

			vi.spyOn(core, "requestSourceFileLoading").mockImplementation(
				async () => {},
			);

			sourceFiles.value = {
				type: "directory",
				children: {
					"a.txt": {
						type: "file",
						content: "before",
						complete: false,
					},
				},
			};

			const { openFile, code } = useSourceFiles(core);

			openFile(["a.txt"]);

			sourceFiles.value = {
				type: "directory",
				children: {
					"a.txt": {
						type: "file",
						content: "after",
						complete: true,
					},
				},
			};
			await flushPromises();

			expect(code.value).toBe("after");
		});
	});
});
