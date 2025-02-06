import { describe, expect, it } from "vitest";
import {
	getJsonSchemaValidator,
	validatorChatBotMessage,
	validatorCssClassname,
	validatorCssSize,
	validatorRepeaterObject,
} from "./validators";

describe("validators", () => {
	describe("CSS Classname", () => {
		const validator = getJsonSchemaValidator(validatorCssClassname);

		it.each([
			"",
			"foo bar",
			"foo",
			"foo bar baz",
			" foo bar ",
			"foo123 bar_baz",
			"class1 class2",
			"foo-bar",
			"foo bar-baz",
		])("should be valid class names: %s", (value) => {
			expect(validator(value)).toBe(true);
		});

		it.each(["123", "-abc"])(
			"should be invalid class names: %s",
			(value) => {
				expect(validator(value)).toBe(false);
			},
		);
	});

	describe("CSS size", () => {
		const validator = getJsonSchemaValidator(validatorCssSize);

		it.each(["", "12px", "1rem", "2vh"])(
			"should be valid size: %s",
			(value) => {
				expect(validator(value)).toBe(true);
			},
		);

		it.each(["px", "vh"])("should be invalid class names: %s", (value) => {
			expect(validator(value)).toBe(false);
		});
	});

	describe("repeater", () => {
		const validator = getJsonSchemaValidator(validatorRepeaterObject);

		it("should validate object", () => {
			expect(validator({ a: { foo: "bar" }, b: { foo: "bar" } })).toBe(
				true,
			);
		});

		it("should validate array", () => {
			expect(validator([{ foo: "bar" }, { foo: "bar" }])).toBe(true);
		});
	});

	describe("chatbot message", () => {
		const validator = getJsonSchemaValidator(validatorChatBotMessage);

		it("should not validate message without role", () => {
			expect(validator({ content: "hello" })).toBe(false);
		});

		it("should validate simple message", () => {
			expect(
				validator({
					role: "assistant",
					content: "hello",
				}),
			).toBe(true);
		});

		it("should validate simple message with more fields", () => {
			expect(
				validator({
					role: "assistant",
					content: "hello",
					foo: "bar",
				}),
			).toBe(true);
		});

		it("should validate message with tools", () => {
			const result = validator({
				role: "assistant",
				content: "hello",
				tools: [
					{
						type: "function",
						function: {
							name: "calculate_mean",
							description:
								"Calculate the mean (average) of a list of numbers.",
							parameters: {
								type: "object",
								properties: {
									numbers: {
										type: "array",
										items: { type: "number" },
										description: "List of numbers",
									},
								},
								required: ["numbers"],
							},
						},
					},
				],
			});
			expect(result).toBe(true);
		});
	});
});
