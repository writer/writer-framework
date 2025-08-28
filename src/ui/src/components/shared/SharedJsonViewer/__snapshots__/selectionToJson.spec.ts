import { describe, it, expect } from "vitest";
import { selectionToJson } from "../selectionToJson";

describe("selectionToJson", () => {
	describe("root object", () => {
		const DATA = {
			name: "JSON Viewer",
			description: "A JSON tree viewer where you can expand the keys.",
			sample: {
				description: "This sample is opened by default",
				bool: true,
				null: null,
				list: [1, "two", { key: 3 }],
			},
			sampleClosed: {
				description: "This sample is not opened by default",
			},
			createdAt: "2025-08-07T12:40:38.362Z",
		} as const;

		const DATA_WITH_EDGE_KEYS = {
			"weird.key[0]?": 123,
			"a+b*c|d^e$": "ops",
			name: "base",
			nameLong: "should not match when only 'name' is selected",
		} as const;

		const EMPTY_SHAPES = {
			emptyObj: {},
			emptyArr: [],
		} as const;

		it("returns empty object when selection has no recognizable tokens", () => {
			const sel = "random text only";
			expect(selectionToJson(DATA, sel)).toEqual({});
		});

		it("returns empty object for blank/whitespace selection", () => {
			const sel = "   \n\r  \n";
			expect(selectionToJson(DATA, sel)).toEqual({});
		});

		it("recognizes CRLF-newline formatting (colon on next line)", () => {
			const sel = `name\r\n:\r\n"JSON Viewer"`;
			expect(selectionToJson(DATA, sel)).toEqual({
				name: DATA.name,
			});
		});

		it("picks a single KV when the line is whole", () => {
			const sel = `"createdAt": "2025-08-07T12:40:38.362Z"`;
			expect(selectionToJson(DATA, sel)).toEqual({
				createdAt: DATA.createdAt,
			});
		});

		it("picks 'name' only when 'description' key is partial", () => {
			const sel = `"name": "JSON Viewer",\n  "desc`;
			expect(selectionToJson(DATA, sel)).toEqual({
				name: DATA.name,
			});
		});

		it("picks full description when its value is partial", () => {
			const sel = `"name": "JSON Viewer",\n  "description": "A JSON tr`;
			expect(selectionToJson(DATA, sel)).toEqual({
				name: DATA.name,
				description: DATA.description,
			});
		});

		it("collapsed parent only -> include full object", () => {
			const sel = `sample\nObject{4}`;
			expect(selectionToJson(DATA, sel)).toEqual({
				sample: DATA.sample,
			});
		});

		it("collapsed window -> include only picked children", () => {
			const sel = `sample
Object{4}
description
:
"This sample is opened by default"
bool
:
true`;
			expect(selectionToJson(DATA, sel)).toEqual({
				sample: {
					description: DATA.sample.description,
					bool: DATA.sample.bool,
				},
			});
		});

		it("collapsed window includes all children (Array[n] counts)", () => {
			const sel = `sample
Object{4}
description
:
"This sample is opened by default"
bool
:
true
null
:
null
list
Array[3]`;
			expect(selectionToJson(DATA, sel)).toEqual({
				sample: DATA.sample,
			});
		});

		it("does not leak root keys that appear inside a collapsed window", () => {
			const sel = `sample
Object{4}
description
:
"This sample is opened by default"
bool
:
true
null
:
null
list
Array[3]`;
			expect(Object.keys(selectionToJson(DATA, sel))).toEqual(["sample"]);
		});

		it("mix of root KVs and a collapsed parent with children", () => {
			const sel = `name
:
"JSON Viewer"
description
:
"A JSON tree viewer where you can expand the keys."
sample
Object{4}
description
:
"This sample is opened by default"
bool
:
true`;
			expect(selectionToJson(DATA, sel)).toEqual({
				name: DATA.name,
				description: DATA.description,
				sample: { description: DATA.sample.description, bool: true },
			});
		});

		it("multiple collapsed + KV after them", () => {
			const sel = `sample
Object{4}
sampleClosed
Object{1}
createdAt
:
"2025-08-07T12:40:38.362Z"`;
			expect(selectionToJson(DATA, sel)).toEqual({
				sample: DATA.sample,
				sampleClosed: DATA.sampleClosed,
				createdAt: DATA.createdAt,
			});
		});

		it("copy whole object when selection effectively covers entire root", () => {
			const sel = `Object{5}
name
:
"JSON Viewer"
description
:
"A JSON tree viewer where you can expand the keys."
sample
Object{4}
description
:
"This sample is opened by default"
bool
:
true
null
:
null
list
Array[3]
sampleClosed
Object{1}
description
:
"This sample is not opened by default"
createdAt
:
"2025-08-07T12:40:38.362Z"`;
			expect(selectionToJson(DATA, sel)).toEqual(DATA);
		});

		it("keys with regex-special characters are matched literally", () => {
			const sel = `"weird.key[0]?"
:
123
"a+b*c|d^e$"
:
"ops"`;
			expect(selectionToJson(DATA_WITH_EDGE_KEYS, sel)).toEqual({
				"weird.key[0]?": DATA_WITH_EDGE_KEYS["weird.key[0]?"],
				"a+b*c|d^e$": DATA_WITH_EDGE_KEYS["a+b*c|d^e$"],
			});
		});

		it("key substring does not match a longer key (exact match only)", () => {
			const sel = `"name": "base"`;
			expect(selectionToJson(DATA_WITH_EDGE_KEYS, sel)).toEqual({
				name: DATA_WITH_EDGE_KEYS.name,
			});
		});

		it("longer key does not accidentally match the shorter one", () => {
			const sel = `"nameLong": "should not match when only 'name' is selected"`;
			expect(selectionToJson(DATA_WITH_EDGE_KEYS, sel)).toEqual({
				nameLong: DATA_WITH_EDGE_KEYS.nameLong,
			});
		});

		it("collapsed empty object/array are included fully", () => {
			const sel1 = `emptyObj\nObject{0}`;
			expect(selectionToJson(EMPTY_SHAPES, sel1)).toEqual({
				emptyObj: {},
			});

			const sel2 = `emptyArr\nArray[0]`;
			expect(selectionToJson(EMPTY_SHAPES, sel2)).toEqual({
				emptyArr: [],
			});
		});

		it("unknown root key in selection is ignored", () => {
			const sel = `ghost\nObject{1}\nname\n:\n"JSON Viewer"`;
			expect(selectionToJson(DATA, sel)).toEqual({
				name: DATA.name,
			});
		});
	});

	describe("root array", () => {
		const DATA = [
			{
				only: "first",
			},
			{
				name: "JSON Viewer",
				description:
					"A JSON tree viewer where you can expand the keys.",
				sample: {
					description: "This sample is opened by default",
					bool: true,
					null: null,
					list: [1, "two", { key: 3 }],
				},
				sampleClosed: {
					description: "This sample is not opened by default",
				},
				createdAt: "2025-08-27T11:29:31.963Z",
			},
		];

		it("Array[n] mention only -> returns full array (copy-all)", () => {
			const sel = `Array[2]`;
			expect(selectionToJson(DATA, sel)).toEqual(DATA);
		});

		it("collapsed index 0 only -> includes element 0 fully", () => {
			const sel = `0\nObject{1}`;
			expect(selectionToJson(DATA, sel)).toEqual([DATA[0]]);
		});

		it("collapsed index 1 with picked children -> includes partial object", () => {
			const sel = `1
Object{5}
description
:
"A JSON tree viewer where you can expand the keys."
sample
Object{4}
description
:
"This sample is opened by default"
bool
:
true`;
			expect(selectionToJson(DATA, sel)).toEqual([
				{
					description:
						"A JSON tree viewer where you can expand the keys.",
					sample: {
						description: "This sample is opened by default",
						bool: true,
					},
				},
			]);
		});

		it("textual order of indices is preserved in the output array", () => {
			const three = [{ i: 0 }, { i: 1 }, { i: 2 }];
			const sel = `2
Object{1}
0
Object{1}`;
			expect(selectionToJson(three, sel)).toEqual([three[2], three[0]]);
		});

		it("negative index is ignored", () => {
			const sel = `-1\nObject{1}`;
			expect(selectionToJson(DATA, sel)).toEqual([]);
		});

		it("index out of bounds is ignored", () => {
			const sel = `2\nObject{1}`;
			expect(selectionToJson(DATA, sel)).toEqual([]);
		});

		it("child key mention without index context does not include anything", () => {
			const sel = `name\n:\n"JSON Viewer"`;
			expect(selectionToJson(DATA, sel)).toEqual([]);
		});

		it("blank selection for root array returns empty array", () => {
			expect(selectionToJson(DATA, "   \n")).toEqual([]);
		});

		it("Array[n] with extra noise still triggers copy-all", () => {
			const sel = `Array[2]\n(not real tokens)`;
			expect(selectionToJson(DATA, sel)).toEqual(DATA);
		});
	});
});
