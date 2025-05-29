import { describe, expect, it } from "vitest";
import {
	buildValidatorBlueprintKeyUniq,
	getJsonSchemaValidator,
	validatorChatBotMessage,
	validatorCssClassname,
	validatorCssSize,
	validatorRepeaterObject,
} from "./validators";
import { buildMockComponent, buildMockCore } from "@/tests/mocks";

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

	describe(buildValidatorBlueprintKeyUniq.name, () => {
		const errorMessage = "Must be unique";
		it("should returns undefined when not blueprint exists", () => {
			const mockCore = buildMockCore();

			expect(
				buildValidatorBlueprintKeyUniq(mockCore.core, "component-id"),
			).toBeUndefined();
		});

		it("should forbid other bluprints keys", () => {
			const mockCore = buildMockCore();

			[1, 2, 3].forEach((i) => {
				mockCore.core.addComponent(
					buildMockComponent({
						id: String(i),
						type: "blueprints_blueprint",
						content: {
							key: String(i),
						},
					}),
				);
			});

			expect(
				buildValidatorBlueprintKeyUniq(mockCore.core, "1"),
			).toStrictEqual({
				errorMessage,
				not: {
					enum: ["2", "3"],
				},
				type: "string",
			});
		});

		it("should handle existing duplicates blueprints keys", () => {
			const mockCore = buildMockCore();

			[2, 2].forEach((i) => {
				mockCore.core.addComponent(
					buildMockComponent({
						id: String(i),
						type: "blueprints_blueprint",
						content: {
							key: String(i),
						},
					}),
				);
			});

			expect(
				buildValidatorBlueprintKeyUniq(mockCore.core, "1"),
			).toStrictEqual({
				errorMessage,
				not: {
					enum: ["2"],
				},
				type: "string",
			});
		});
	});
});
