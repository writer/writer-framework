import { describe, it, expect } from "vitest";
import { deepMerge, getValueAtPath, setValueAtPath } from "./object";

describe("setValueAtPath", () => {
	it("should set a top-level property", () => {
		const obj: Record<string, unknown> = {};
		setValueAtPath(obj, "name", "Alice");
		expect(obj).toEqual({ name: "Alice" });
	});

	it("should set a deeply nested property", () => {
		const obj: Record<string, unknown> = {};
		setValueAtPath(obj, "user.profile.age", 30);
		expect(obj).toEqual({ user: { profile: { age: 30 } } });
	});

	it("should overwrite an existing property", () => {
		const obj: Record<string, unknown> = {
			user: { profile: { name: "Alice" } },
		};
		setValueAtPath(obj, "user.profile.name", "Bob");
		expect(obj).toEqual({ user: { profile: { name: "Bob" } } });
	});

	it("should not overwrite sibling properties", () => {
		const obj: Record<string, unknown> = {
			user: { profile: { name: "Alice" } },
		};
		setValueAtPath(obj, "user.profile.age", 25);
		expect(obj).toEqual({ user: { profile: { name: "Alice", age: 25 } } });
	});

	it("should handle path overwriting a primitive with an object", () => {
		const obj: Record<string, unknown> = { user: "notAnObject" };
		setValueAtPath(obj, "user.profile.name", "Charlie");
		expect(obj).toEqual({ user: { profile: { name: "Charlie" } } });
	});

	it("should overwrite a null value on the path with an object", () => {
		const obj: Record<string, unknown> = { settings: null };
		setValueAtPath(obj, "settings.theme", "dark");
		expect(obj).toEqual({ settings: { theme: "dark" } });
	});

	it("should overwrite an array with an object if part of the path is an array", () => {
		const obj: Record<string, unknown> = { items: [] };
		setValueAtPath(obj, "items.name", "item1");
		expect(obj).toEqual({ items: { name: "item1" } });
	});

	it("should handle empty path gracefully (no-op)", () => {
		const obj: Record<string, unknown> = { x: 1 };
		setValueAtPath(obj, "", "value");
		expect(obj).toEqual({ x: 1 }); // unchanged
	});

	it.each(["__proto__", "constructor", "prototype", "hasOwnProperty"])(
		"should prevent Prototype-polluting with path=%s",
		(key) => {
			const obj: Record<string, unknown> = { x: 1 };
			expect(() => setValueAtPath(obj, key, "value")).toThrow();
		},
	);
});

describe(getValueAtPath, () => {
	it("should return a top-level value", () => {
		const obj = { name: "Alice" };
		expect(getValueAtPath(obj, "name")).toBe("Alice");
	});

	it("should return a deeply nested value", () => {
		const obj = { user: { profile: { age: 30 } } };
		expect(getValueAtPath(obj, "user.profile.age")).toBe(30);
	});

	it("should return undefined for missing property", () => {
		const obj = { user: { profile: {} } };
		expect(getValueAtPath(obj, "user.profile.age")).toBeUndefined();
	});

	it("should return undefined if path leads through a primitive", () => {
		const obj = { user: "string" };
		expect(getValueAtPath(obj, "user.name")).toBeUndefined();
	});

	it("should return undefined for empty path", () => {
		const obj = { x: 1 };
		expect(getValueAtPath(obj, "")).toBeUndefined();
	});

	it("should return undefined if root is null", () => {
		expect(getValueAtPath(null as any, "a.b")).toBeUndefined();
	});

	it("should return undefined if key exists but value is undefined", () => {
		const obj = { a: { b: undefined } };
		expect(getValueAtPath(obj, "a.b")).toBeUndefined();
	});

	it("should work with falsy values (e.g. 0, false)", () => {
		const obj = { a: { b: false, c: 0 } };
		expect(getValueAtPath(obj, "a.b")).toBe(false);
		expect(getValueAtPath(obj, "a.c")).toBe(0);
	});
});

describe(deepMerge, () => {
	it("merges flat objects", () => {
		const a = { x: 1 };
		const b = { y: 2 };
		expect(deepMerge(a, b)).toEqual({ x: 1, y: 2 });
	});

	it("overwrites primitive values from source", () => {
		const a = { x: 1 };
		const b = { x: 2 };
		expect(deepMerge(a, b)).toEqual({ x: 2 });
	});

	it("overwrites primitive values with object from source", () => {
		const a = { x: 1 };
		const b = { x: { y: "z" } };
		expect(deepMerge(a, b)).toEqual({ x: { y: "z" } });
	});

	it("merges nested objects", () => {
		const a = { user: { name: "Alice" } };
		const b = { user: { age: 30 } };
		expect(deepMerge(a, b)).toEqual({ user: { name: "Alice", age: 30 } });
	});

	it("overwrites arrays by default", () => {
		const a = { items: [1, 2] };
		const b = { items: [3] };
		expect(deepMerge(a, b)).toEqual({ items: [3] });
	});

	it("handles nulls and undefined safely", () => {
		const a = { a: null };
		const b = { a: { nested: true } };
		expect(deepMerge(a, b)).toEqual({ a: { nested: true } });

		const c = { a: { nested: true } };
		const d = { a: null };
		expect(deepMerge(c, d)).toEqual({ a: null });
	});

	it("does not mutate input objects", () => {
		const a = { x: { y: 1 } };
		const b = { x: { z: 2 } };
		const merged = deepMerge(a, b);
		expect(merged).toEqual({ x: { y: 1, z: 2 } });
		expect(a).toEqual({ x: { y: 1 } });
		expect(b).toEqual({ x: { z: 2 } });
	});
});
