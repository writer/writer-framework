import {
	SourceFilesFile,
	SourceFilesBinary,
	SourceFilesDirectory,
	SourceFiles,
} from "@/writerTypes";

export function isSourceFilesFile(value: unknown): value is SourceFilesFile {
	if (typeof value !== "object" || value === null) return false;
	return value["type"] === "file" && typeof value["content"] === "string";
}

export function isSourceFilesBinary(
	value: unknown,
): value is SourceFilesBinary {
	if (typeof value !== "object" || value === null) return false;
	return value["type"] === "binary";
}

export function isSourceFilesDirectory(
	value: unknown,
): value is SourceFilesDirectory {
	if (typeof value !== "object" || value === null) return false;
	return (
		value["type"] === "directory" && typeof value["children"] === "object"
	);
}

/**
 * Generate all the possible paths leading to a file
 */
export function* getSourceFilesPathsToFiles(
	tree: SourceFiles,
	path: string[] = [],
): Generator<string[]> {
	if (!isSourceFilesDirectory(tree)) {
		yield path;
		return;
	}

	for (const [root, node] of Object.entries(tree.children)) {
		yield* getSourceFilesPathsToFiles(node, [...path, root]);
	}
}

/**
 * Generate all the possible paths leading to an edge (file or folder)
 */
export function* getSourceFilesPathsToEdges(
	tree: SourceFiles,
	path: string[] = [],
): Generator<string[]> {
	if (isSourceFilesFile(tree)) {
		yield path;
		return;
	}
	if (Object.values(tree.children).length === 0) {
		yield path;
		return;
	}

	for (const [root, node] of Object.entries(tree.children)) {
		yield* getSourceFilesPathsToEdges(node, [...path, root]);
	}
}

/**
 * Generate all the possible paths
 */
export function* getSourceFilesPathsToNodes(
	tree: SourceFiles,
	path: string[] = [],
): Generator<string[]> {
	yield path;
	if (!isSourceFilesDirectory(tree)) return;

	for (const [root, node] of Object.entries(tree.children)) {
		yield* getSourceFilesPathsToNodes(node, [...path, root]);
	}
}

export function findSourceFileFromPath(
	path: string[],
	tree: SourceFiles,
): SourceFilesDirectory | SourceFilesFile | SourceFilesBinary | undefined {
	if (path.length === 0) return tree;
	if (!isSourceFilesDirectory(tree)) return undefined;

	const [key, ...restPath] = path;
	const node = tree.children[key];

	return restPath.length === 0
		? node
		: findSourceFileFromPath(restPath, node);
}

export function createFileToSourceFiles(
	path: string[],
	tree: SourceFiles,
	newFile: SourceFilesFile = {
		type: "file",
		content: "",
		complete: true,
	},
) {
	const copy = structuredClone(tree);
	let node = copy;

	for (let i = 0; i < path.length; i++) {
		if (!isSourceFilesDirectory(node)) return copy;

		const key = path.at(i);

		if (i === path.length - 1) {
			node.children[key] = newFile;
			return copy;
		} else {
			node.children[key] ??= { type: "directory", children: {} };
			node = node.children[key];
		}
	}

	return copy;
}

export function moveFileToSourceFiles(
	fromPath: string[],
	toPath: string[],
	tree: SourceFiles,
) {
	const node = findSourceFileFromPath(fromPath, tree);
	if (isSourceFilesDirectory(node) || node === undefined) return tree;

	const treeWithDelete = deleteFileToSourceFiles(fromPath, tree);
	return createFileToSourceFiles(
		toPath,
		treeWithDelete,
		structuredClone(node),
	);
}

export function deleteFileToSourceFiles(path: string[], tree: SourceFiles) {
	const copy = structuredClone(tree);
	let node = copy;

	for (let i = 0; i < path.length; i++) {
		if (!isSourceFilesDirectory(node)) return copy;

		const key = path.at(i);

		if (!(key in node.children)) return copy;

		if (i === path.length - 1) {
			delete node.children[key];
			return copy;
		} else {
			node.children[key] ??= { type: "directory", children: {} };
			node = node.children[key];
		}
	}

	return copy;
}
