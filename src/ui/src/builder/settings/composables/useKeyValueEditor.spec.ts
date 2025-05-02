import { describe, expect, it } from "vitest";
import { useKeyValueEditor } from "./useKeyValueEditor";

describe(useKeyValueEditor.name, () => {
	describe("assisted mode", () => {
		it("should get invalid status when keys are duplicated", () => {
			const {
				assistedEntries,
				isValid,
				addAssistedEntry,
				updateAssistedEntryKey,
				getAssistedEntryError,
			} = useKeyValueEditor({ foo: "bar" });

			expect(assistedEntries.value).toStrictEqual({
				1: { key: "foo", value: "bar" },
			});

			addAssistedEntry();
			updateAssistedEntryKey("2", "foo");

			expect(assistedEntries.value).toStrictEqual({
				1: { key: "foo", value: "bar" },
				2: { key: "foo", value: "" },
			});

			expect(isValid.value).toBe(false);

			expect(getAssistedEntryError("1")).toBe(
				"This key is already in use. Please remove duplicate keys.",
			);
		});

		it("shoul update an entry", () => {
			const {
				assistedEntries,
				addAssistedEntry,
				isValid,
				updateAssistedEntryValue,
				updateAssistedEntryKey,
			} = useKeyValueEditor({ foo: "bar" });

			expect(assistedEntries.value).toStrictEqual({
				1: { key: "foo", value: "bar" },
			});

			addAssistedEntry();

			expect(assistedEntries.value).toStrictEqual({
				1: { key: "foo", value: "bar" },
				2: { key: "", value: "" },
			});
			expect(isValid.value).toBe(true);

			updateAssistedEntryKey("2", "test");
			updateAssistedEntryValue("2", "test");

			expect(assistedEntries.value).toStrictEqual({
				1: { key: "foo", value: "bar" },
				2: { key: "test", value: "test" },
			});
		});

		it("shoul delete an entry", () => {
			const { assistedEntries, removeAssistedEntry } = useKeyValueEditor({
				foo: "bar",
			});

			removeAssistedEntry("1");

			expect(assistedEntries.value).toStrictEqual({});
		});
	});

	describe("freehand mode", () => {
		it("should handle invalid JSON", () => {
			const { mode, freehandValue, currentValue, isValid } =
				useKeyValueEditor({
					foo: "bar",
				});
			mode.value = "freehand";

			freehandValue.value = '{"foo';
			expect(currentValue.value).toStrictEqual({});
			expect(isValid.value).toBe(false);
		});

		it("should reflect changes when moving from freehand mode to assisted mode", () => {
			const { assistedEntries, mode, freehandValue } = useKeyValueEditor({
				foo: "bar",
			});
			mode.value = "freehand";
			freehandValue.value = JSON.stringify({ hello: "world" });

			mode.value = "assisted";

			expect(assistedEntries.value).toStrictEqual({
				2: { key: "hello", value: "world" },
			});
		});
	});

	describe("mode change", () => {
		it("should reflect changes when moving from assisted mode to freehand mode", () => {
			const {
				assistedEntries,
				mode,
				freehandValue,
				updateAssistedEntryKey,
				currentValue,
			} = useKeyValueEditor({ foo: "bar" });

			expect(assistedEntries.value).toStrictEqual({
				1: { key: "foo", value: "bar" },
			});

			updateAssistedEntryKey("1", "hello");

			mode.value = "freehand";

			expect(freehandValue.value).toStrictEqual(
				JSON.stringify({ hello: "bar" }, undefined, 2),
			);
			expect(currentValue.value).toStrictEqual({ hello: "bar" });
		});

		it("should reflect changes when moving from freehand mode to assisted mode", () => {
			const { assistedEntries, mode, freehandValue } = useKeyValueEditor({
				foo: "bar",
			});
			mode.value = "freehand";
			freehandValue.value = JSON.stringify({ hello: "world" });

			mode.value = "assisted";

			expect(assistedEntries.value).toStrictEqual({
				2: { key: "hello", value: "world" },
			});
		});
	});
});
