/**
 * JSON serializer to handle bigint
 */
export function bigIntReplacer(_key: string, value: unknown): unknown {
	if (typeof value === "bigint") {
		return value.toString() + "n";
	}
	return value;
}
