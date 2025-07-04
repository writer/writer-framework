import { describe, expect, it, vi, beforeAll, afterAll } from "vitest";
import { convertAbsolutePathtoFullURL, resolveAssetURL } from "./url";

describe(convertAbsolutePathtoFullURL.name, () => {
	it("should convert the URL", () => {
		expect(
			convertAbsolutePathtoFullURL(
				"/assets/image.png",
				"http://localhost:3000/",
			),
		).toBe("http://localhost:3000/assets/image.png");
	});

	it("should convert the URL with a current path", () => {
		expect(
			convertAbsolutePathtoFullURL(
				"/assets/image.png",
				"http://localhost:3000/hello/?foo=bar",
			),
		).toBe("http://localhost:3000/hello/assets/image.png");
	});
});

describe(resolveAssetURL.name, () => {
	beforeAll(() => {
		vi.stubGlobal("location", new URL("http://localhost:3000/"));
	});

	afterAll(() => {
		vi.unstubAllGlobals();
	});

	it("Should build the absolute URL from the absolute path", () => {
		expect(resolveAssetURL("/assets/image.png")).toBe(
			"http://localhost:3000/assets/image.png",
		);
	});

	it("Should not change the relative path", () => {
		expect(resolveAssetURL("./assets/image.png")).toBe(
			"./assets/image.png",
		);
	});

	it("Should not change the relative path without leading .", () => {
		expect(resolveAssetURL("assets/image.png")).toBe("assets/image.png");
	});

	it("Should not change the absolute path", () => {
		expect(resolveAssetURL("http://someserver/assets/image.png")).toBe(
			"http://someserver/assets/image.png",
		);
	});
});
