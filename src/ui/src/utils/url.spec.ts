import { describe, expect, it } from "vitest";
import { convertAbsolutePathtoFullURL } from "./url";

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
