import { describe, it, expect } from "vitest";

import {
	createFileToSourceFiles,
	deleteFileToSourceFiles,
	findSourceFileFromPath,
	getSourceFilesPathsToEdges,
	getSourceFilesPathsToFiles,
	moveFileToSourceFiles,
} from "./sourceFiles";
import { SourceFiles, SourceFilesFile } from "@/writerTypes.js";

describe(findSourceFileFromPath.name, () => {
	it("should retreive from simple path", () => {
		const file: SourceFilesFile = {
			type: "file",
			content: "a",
		};

		const tree: SourceFiles = {
			type: "directory",
			children: { file },
		};

		expect(findSourceFileFromPath(["file"], tree)).toBe(file);
	});

	it("should retreive from nested path", () => {
		const file: SourceFilesFile = {
			type: "file",
			content: "a",
		};

		const tree: SourceFiles = {
			type: "directory",
			children: {
				a: {
					type: "directory",
					children: { b: { type: "directory", children: { file } } },
				},
			},
		};

		expect(findSourceFileFromPath(["a", "b", "file"], tree)).toBe(file);
	});
});

describe(getSourceFilesPathsToEdges.name, () => {
	it("should generate all nestes path", () => {
		const result = getSourceFilesPathsToEdges({
			type: "directory",
			children: {
				"a.txt": {
					type: "file",
					content: "",
				},
				b: {
					type: "directory",
					children: {
						c: {
							type: "directory",
							children: {
								"d.txt": {
									type: "file",
									content: "",
								},
								e: {
									type: "directory",
									children: {},
								},
							},
						},
					},
				},
			},
		});

		expect(Array.from(result)).toStrictEqual([
			["a.txt"],
			["b", "c", "d.txt"],
			["b", "c", "e"],
		]);
	});
});

describe(getSourceFilesPathsToFiles.name, () => {
	it("should generate simple path", () => {
		const result = getSourceFilesPathsToFiles({
			type: "directory",
			children: {
				"a.txt": {
					type: "file",
					content: "",
				},
				"b.txt": {
					type: "file",
					content: "",
				},
			},
		});

		expect(Array.from(result)).toStrictEqual([["a.txt"], ["b.txt"]]);
	});

	it("should generate all nestes path", () => {
		const result = getSourceFilesPathsToFiles({
			type: "directory",
			children: {
				"a.txt": {
					type: "file",
					content: "",
				},
				b: {
					type: "directory",
					children: {
						c: {
							type: "directory",
							children: {
								"d.txt": {
									type: "file",
									content: "",
								},
								e: {
									type: "directory",
									children: {},
								},
							},
						},
					},
				},
			},
		});

		expect(Array.from(result)).toStrictEqual([
			["a.txt"],
			["b", "c", "d.txt"],
		]);
	});
});

describe(createFileToSourceFiles.name, () => {
	it("should create the file", () => {
		const result = createFileToSourceFiles(["a", "b", "c.txt"], {
			type: "directory",
			children: {},
		});

		expect(result).toStrictEqual({
			type: "directory",
			children: {
				a: {
					type: "directory",
					children: {
						b: {
							type: "directory",
							children: {
								"c.txt": {
									type: "file",
									content: "",
									complete: true,
								},
							},
						},
					},
				},
			},
		});
	});
});

describe(moveFileToSourceFiles.name, () => {
	it("should move file", () => {
		const initial: SourceFiles = {
			type: "directory",
			children: {
				a: {
					type: "directory",
					children: {
						"b.txt": {
							type: "file",
							content: "",
							complete: true,
						},
					},
				},
			},
		};
		const result = moveFileToSourceFiles(
			["a", "b.txt"],
			["b", "b.txt"],
			initial,
		);

		expect(result).toStrictEqual({
			type: "directory",
			children: {
				a: {
					type: "directory",
					children: {},
				},
				b: {
					type: "directory",
					children: {
						"b.txt": {
							type: "file",
							content: "",
							complete: true,
						},
					},
				},
			},
		});
	});

	it("should move binary", () => {
		const initial: SourceFiles = {
			type: "directory",
			children: {
				a: {
					type: "directory",
					children: {
						"b.png": {
							type: "binary",
						},
					},
				},
			},
		};
		const result = moveFileToSourceFiles(
			["a", "b.png"],
			["b", "b.png"],
			initial,
		);

		expect(result).toStrictEqual({
			type: "directory",
			children: {
				a: {
					type: "directory",
					children: {},
				},
				b: {
					type: "directory",
					children: {
						"b.png": {
							type: "binary",
						},
					},
				},
			},
		});
	});
});

describe(deleteFileToSourceFiles.name, () => {
	const initial: SourceFiles = {
		type: "directory",
		children: {
			a: {
				type: "directory",
				children: {
					"b.txt": {
						type: "file",
						content: "",
						complete: true,
					},
				},
			},
		},
	};

	it("should delete the file", () => {
		const result = deleteFileToSourceFiles(["a", "b.txt"], initial);

		expect(result).toStrictEqual({
			type: "directory",
			children: {
				a: {
					type: "directory",
					children: {},
				},
			},
		});
	});

	it("should delete the directory", () => {
		const result = deleteFileToSourceFiles(["a"], initial);

		expect(result).toStrictEqual({
			type: "directory",
			children: {},
		});
	});

	it("should handle unexisting path", () => {
		const result = deleteFileToSourceFiles(["x", "y"], initial);

		expect(result).toStrictEqual(initial);
	});
});
