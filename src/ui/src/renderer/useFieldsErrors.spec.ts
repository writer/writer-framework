import { describe, vi, it, expect, beforeAll } from "vitest";
import { useFieldsErrors } from "./useFieldsErrors";
import { computed, ref } from "vue";
import { generateCore } from "@/core";
import {
	Core,
	FieldType,
	InstancePath,
	WriterComponentDefinition,
} from "@/writerTypes";
import { validatorCustomSchemas } from "@/constants/validators";

const getEvaluatedFields = vi.fn();

vi.mock("./useEvaluator", () => ({
	useEvaluator: () => ({ getEvaluatedFields }),
}));

describe(useFieldsErrors.name, () => {
	const instancePath = computed<InstancePath>(() => [
		{
			componentId: "1",
			instanceNumber: 0,
		},
	]);
	let core: Core;

	const dummyComponent: WriterComponentDefinition = {
		name: "dummmy component",
		description: "",
	};

	beforeAll(() => {
		core = generateCore();
		// @ts-expect-error return a dummy mock
		vi.spyOn(core, "getComponentById").mockReturnValue({});
	});

	it("should validate a field as number", () => {
		vi.spyOn(core, "getComponentDefinition").mockReturnValue({
			...dummyComponent,
			fields: {
				value: {
					name: "value",
					type: FieldType.Number,
					validator: {
						type: "number",
						minimum: 10,
					},
				},
			},
		});

		const value = ref(1);
		getEvaluatedFields.mockReturnValue({ value });

		const errors = useFieldsErrors(core, instancePath);
		expect(errors.value).toStrictEqual({ value: "must be >= 10" });

		value.value = 10;

		expect(errors.value).toStrictEqual({ value: undefined });
	});

	it("should validate a field as string", () => {
		vi.spyOn(core, "getComponentDefinition").mockReturnValue({
			...dummyComponent,
			fields: {
				value: {
					name: "value",
					type: FieldType.Text,
					validator: {
						type: "string",
						format: "uri",
					},
				},
			},
		});

		const value = ref("test");
		getEvaluatedFields.mockReturnValue({ value });

		const errors = useFieldsErrors(core, instancePath);
		expect(errors.value).toStrictEqual({
			value: validatorCustomSchemas.uri.errorMessage,
		});

		value.value = "https://writer.com";

		expect(errors.value).toStrictEqual({ value: undefined });
	});

	it("should validate a field as options", () => {
		vi.spyOn(core, "getComponentDefinition").mockReturnValue({
			...dummyComponent,
			fields: {
				value: {
					name: "value",
					type: FieldType.Text,
					options: {
						a: "A",
						b: "B",
						c: "C",
					},
				},
			},
		});

		const value = ref("test");
		getEvaluatedFields.mockReturnValue({ value });

		const errors = useFieldsErrors(core, instancePath);
		expect(errors.value).toStrictEqual({
			value: "must be equal to one of the allowed values: a, b, c",
		});

		value.value = "a";

		expect(errors.value).toStrictEqual({ value: undefined });
	});
});
