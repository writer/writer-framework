import { beforeEach, describe, expect, it, MockInstance, vi } from "vitest";
import { useSourceFiles } from "./useSourceFiles";
import { buildMockCore } from "@/tests/mocks";
import { flushPromises } from "@vue/test-utils";
import { generateCore } from ".";

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

	it("should remove a folder to the draft", async () => {
		const { core, sourceFiles } = buildMockCore();
		sourceFiles.value = {
			type: "directory",
			children: {
				a: {
					type: "directory",
					children: {
						b: { type: "directory", children: {} },
						"c.txt": { type: "file", content: "" },
					},
				},
			},
		};

		const { sourceFileDraft } = useSourceFiles(core);
		expect(sourceFileDraft.value).toStrictEqual(sourceFiles.value);

		sourceFiles.value = {
			type: "directory",
			children: {
				a: {
					type: "directory",
					children: {
						"c.txt": { type: "file", content: "" },
					},
				},
			},
		};
		await flushPromises();
		expect(sourceFileDraft.value).toStrictEqual(sourceFiles.value);
	});

	it("should remove a root folder to the draft", async () => {
		const { core, sourceFiles } = buildMockCore();
		sourceFiles.value = {
			type: "directory",
			children: {
				a: {
					type: "directory",
					children: {
						b: { type: "directory", children: {} },
						"c.txt": { type: "file", content: "" },
					},
				},
			},
		};

		const { sourceFileDraft } = useSourceFiles(core);
		expect(sourceFileDraft.value).toStrictEqual(sourceFiles.value);

		sourceFiles.value = { type: "directory", children: {} };
		await flushPromises();
		expect(sourceFileDraft.value).toStrictEqual(sourceFiles.value);
	});

	describe("save", () => {
		let mockCore: ReturnType<typeof buildMockCore>;

		beforeEach(() => {
			mockCore = buildMockCore();

			vi.spyOn(mockCore.core, "sendCodeSaveRequest").mockImplementation(
				async () => {},
			);

			vi.spyOn(
				mockCore.core,
				"sendRenameSourceFileRequest",
			).mockImplementation(async () => {});
		});

		describe("text file", () => {
			beforeEach(() => {
				mockCore.sourceFiles.value = {
					type: "directory",
					children: {
						"a.txt": {
							type: "file",
							content: "A",
							complete: true,
						},
					},
				};
			});

			it("should save", async () => {
				const { openFile, save } = useSourceFiles(mockCore.core);

				openFile(["a.txt"]);
				await save();

				expect(
					mockCore.core.sendCodeSaveRequest,
				).toHaveBeenNthCalledWith(1, "A", ["a.txt"]);
				expect(
					mockCore.core.sendRenameSourceFileRequest,
				).not.toHaveBeenCalled();
			});

			it("should save and rename", async () => {
				const { openFile, save } = useSourceFiles(mockCore.core);

				openFile(["a.txt"]);
				await save(["b.txt"]);

				expect(
					mockCore.core.sendCodeSaveRequest,
				).toHaveBeenNthCalledWith(1, "A", ["a.txt"]);
				expect(
					mockCore.core.sendRenameSourceFileRequest,
				).toHaveBeenNthCalledWith(1, ["a.txt"], ["b.txt"]);
			});
		});

		describe("binary file", () => {
			beforeEach(() => {
				mockCore.sourceFiles.value = {
					type: "directory",
					children: {
						"a.png": {
							type: "binary",
						},
					},
				};
			});

			it("should save", async () => {
				const { openFile, save } = useSourceFiles(mockCore.core);

				openFile(["a.png"]);
				await save();

				expect(
					mockCore.core.sendCodeSaveRequest,
				).not.toHaveBeenCalled();
				expect(
					mockCore.core.sendRenameSourceFileRequest,
				).not.toHaveBeenCalled();
			});

			it("should save and rename", async () => {
				const { openFile, save } = useSourceFiles(mockCore.core);

				openFile(["a.png"]);
				await save(["b.png"]);

				expect(
					mockCore.core.sendCodeSaveRequest,
				).not.toHaveBeenCalled();
				expect(
					mockCore.core.sendRenameSourceFileRequest,
				).toHaveBeenNthCalledWith(1, ["a.png"], ["b.png"]);
			});
		});
	});

	describe("upload", () => {
		let mockCore: ReturnType<typeof buildMockCore>;

		beforeEach(() => {
			mockCore = buildMockCore();

			vi.spyOn(mockCore.core, "sendFileUploadRequest").mockImplementation(
				async () => {},
			);
		});

		it("should not overide an existing file", async () => {
			mockCore.sourceFiles.value = {
				type: "directory",
				children: {
					"a.txt": {
						type: "file",
						content: "A",
						complete: false,
					},
				},
			};

			const { upload } = useSourceFiles(mockCore.core);
			const files = [new File([], "a.txt")] as unknown as FileList;

			await expect(upload(files)).rejects.toThrowError(
				"The file a.txt already exists",
			);

			expect(mockCore.core.sendFileUploadRequest).not.toHaveBeenCalled();
		});

		it("should not upload big file", async () => {
			const { upload } = useSourceFiles(mockCore.core);

			const fileSize = 200 * 1024 * 1024; // 200mb

			const files = [
				{
					...new File([], "a.png"),
					size: fileSize,
				},
			] as unknown as FileList;

			await expect(upload(files)).rejects.toThrowError(
				/Cannot upload file bigger than/,
			);

			expect(mockCore.core.sendFileUploadRequest).not.toHaveBeenCalled();
		});

		it("should upload a text file", async () => {
			const { upload } = useSourceFiles(mockCore.core);
			const files = [new File(["Hello"], "a.txt")] as unknown as FileList;

			await upload(files);

			expect(mockCore.core.sendFileUploadRequest).toHaveBeenCalledOnce();
			expect(mockCore.core.sendFileUploadRequest).toHaveBeenCalledWith(
				["a.txt"],
				"Hello",
			);
		});

		it("should upload a binary file", async () => {
			const { upload } = useSourceFiles(mockCore.core);

			const binaryData = new Uint8Array([72, 101, 108, 108, 111]); // "Hello" in ASCII
			const files = [
				new File([binaryData], "a.png"),
			] as unknown as FileList;

			await upload(files);

			expect(mockCore.core.sendFileUploadRequest).toHaveBeenCalledOnce();
			expect(mockCore.core.sendFileUploadRequest).toHaveBeenCalledWith(
				["a.png"],
				"Hello",
			);
		});
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
