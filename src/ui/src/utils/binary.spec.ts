import { describe, it, expect } from "vitest";
import { formatBytes } from "./binary";

describe(formatBytes.name, () => {
	it("handles zero", () => {
		expect(formatBytes(0)).toBe("0 B");
		expect(formatBytes(0, { minUnit: "KB" })).toBe("0 KB");
	});

	it("converts bytes correctly", () => {
		expect(formatBytes(1)).toBe("1 B");
		expect(formatBytes(1023)).toBe("1023 B");
		expect(formatBytes(2 * 1024)).toBe("2.0 KB");
		expect(formatBytes(4 * 1024 * 1024)).toBe("4.0 MB");
		expect(formatBytes(9_876_543_210)).toBe("9.2 GB");
	});

	it("exact 1 KB boundary uses 1 decimal in smart mode", () => {
		expect(formatBytes(1024)).toBe("1.0 KB");
	});

	it("values <10 in chosen unit show 1 decimal in smart mode", () => {
		expect(formatBytes(1536)).toBe("1.5 KB");
		expect(formatBytes(9.5 * 1024 * 1024)).toBe("9.5 MB");
	});

	it("values >=10 in chosen unit show 0 decimals in smart mode", () => {
		expect(formatBytes(10 * 1024)).toBe("10 KB");
		expect(formatBytes(12 * 1024 * 1024)).toBe("12 MB");
	});

	it("rounding near unit threshold (no carry to next unit)", () => {
		expect(formatBytes(1024 * 1024 - 1)).toBe("1024 KB");
	});

	it("decimals option overrides smart", () => {
		expect(formatBytes(1024)).toBe("1.0 KB");
		expect(formatBytes(1024, { decimals: 0 })).toBe("1 KB");

		expect(formatBytes(1_234_567)).toBe("1.2 MB");
		expect(formatBytes(1_234_567, { decimals: 2 })).toBe("1.18 MB");
	});

	it("does not go below minUnit", () => {
		expect(formatBytes(512)).toBe("512 B");
		expect(formatBytes(512, { minUnit: "KB" })).toBe("0.5 KB");
		expect(formatBytes(512, { minUnit: "MB" })).toBe("0.0 MB");
		expect(formatBytes(512, { minUnit: "MB", decimals: 4 })).toBe(
			"0.0005 MB",
		);
	});

	it("does not go above maxUnit", () => {
		expect(formatBytes(1024 * 1024, { maxUnit: "KB" })).toBe("1024 KB");
		expect(formatBytes(1000 * 1024 * 1024 * 1024, { maxUnit: "GB" })).toBe(
			"1000 GB",
		);
	});

	it('invalid inputs return "-"', () => {
		expect(formatBytes(Number.NaN)).toBe("-");
		expect(formatBytes(Number.POSITIVE_INFINITY)).toBe("-");
		expect(formatBytes(Number.NEGATIVE_INFINITY)).toBe("-");
		expect(formatBytes(-1)).toBe("-");
	});
});
