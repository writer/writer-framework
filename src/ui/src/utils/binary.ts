export type ByteUnit = "B" | "KB" | "MB" | "GB";
const UNITS: ByteUnit[] = ["B", "KB", "MB", "GB"];

export interface FormatBytesOptions {
	minUnit?: ByteUnit;
	maxUnit?: ByteUnit;
	decimals?: number | "smart";
}

export function formatBytes(
	bytesInput: number,
	{ minUnit, maxUnit, decimals = "smart" }: FormatBytesOptions = {},
): string {
	const bytes =
		typeof bytesInput === "number" ? bytesInput : Number(bytesInput);

	if (!Number.isFinite(bytes) || bytes < 0) {
		return "-";
	}

	const minUnitIdx = minUnit ? Math.max(0, UNITS.indexOf(minUnit)) : 0;

	if (bytes === 0) {
		return `0 ${UNITS[minUnitIdx]}`;
	}

	const maxUnitIdx = maxUnit
		? Math.min(UNITS.indexOf(maxUnit), UNITS.length - 1)
		: UNITS.length - 1;

	let unitIndex = minUnitIdx;
	let value = bytes;

	for (let i = 0; i < minUnitIdx; i++) {
		value /= 1024;
	}

	while (value >= 1024 && unitIndex < maxUnitIdx) {
		value /= 1024;
		unitIndex++;
	}

	let fractionDigits: number;

	if (decimals === "smart") {
		if (unitIndex === 0) {
			fractionDigits = 0;
		} else {
			fractionDigits = value < 10 ? 1 : 0;
		}
	} else {
		fractionDigits = Math.max(0, Math.min(6, decimals));
	}

	const result =
		fractionDigits > 0
			? value.toFixed(fractionDigits)
			: Math.round(value).toString();

	return `${result} ${UNITS[unitIndex]}`;
}
