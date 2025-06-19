import { describe, vi, it, expect, beforeAll } from "vitest";
import { useFieldsErrors } from "./useFieldsErrors";
import { computed, ref } from "vue";
import {
	FieldType,
	InstancePath,
	WriterComponentDefinition,
} from "@/writerTypes";
import { validatorCustomSchemas } from "@/constants/validators";
import { buildMockComponent, buildMockCore } from "@/tests/mocks";

const getEvaluatedFields = vi.fn();

vi.mock("./useEvaluator", async () => {
	const actual = await vi.importActual("./useEvaluator");
	return {
		...actual,
		useEvaluator: () => ({ getEvaluatedFields }),
	};
});

describe(useFieldsErrors.name, () => {
	const instancePath = computed<InstancePath>(() => [
		{
			componentId: "1",
			instanceNumber: 0,
		},
	]);
	let mockCore: ReturnType<typeof buildMockCore>;

	const dummyComponent: WriterComponentDefinition = {
		name: "dummmy component",
		description: "",
	};

	function mockComponentFieldValue<T>(value: T) {
		const valueRef = ref(value);
		getEvaluatedFields.mockReturnValue({ value: valueRef });
		mockCore.core.getComponentById("1").content = {
			value: String(value),
		};
		return valueRef;
	}

	beforeAll(() => {
		mockCore = buildMockCore();

		mockCore.core.addComponent(
			buildMockComponent({
				id: "1",
			}),
		);
	});

	it("should validate a field as number", () => {
		vi.spyOn(mockCore.core, "getComponentDefinition").mockReturnValue({
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

		const value = mockComponentFieldValue(1);

		const errors = useFieldsErrors(mockCore.core, instancePath);
		expect(errors.value).toStrictEqual({ value: "must be >= 10" });

		value.value = 10;

		expect(errors.value).toStrictEqual({ value: undefined });
	});

	it("should validate a field as string", () => {
		vi.spyOn(mockCore.core, "getComponentDefinition").mockReturnValue({
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

		const value = mockComponentFieldValue("test");

		const errors = useFieldsErrors(mockCore.core, instancePath);
		expect(errors.value).toStrictEqual({
			value: validatorCustomSchemas.uri.errorMessage,
		});

		value.value = "https://writer.com";

		expect(errors.value).toStrictEqual({ value: undefined });
	});

	it("should not validate a field containing a template expression", () => {
		vi.spyOn(mockCore.core, "getComponentDefinition").mockReturnValue({
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

		const value = mockComponentFieldValue("test");

		const errors = useFieldsErrors(mockCore.core, instancePath);
		expect(errors.value).toStrictEqual({
			value: validatorCustomSchemas.uri.errorMessage,
		});

		value.value = "https://writer.com";

		expect(errors.value).toStrictEqual({ value: undefined });
	});

	it("should validate a field as options", () => {
		vi.spyOn(mockCore.core, "getComponentDefinition").mockReturnValue({
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

		const value = mockComponentFieldValue("test");

		const errors = useFieldsErrors(mockCore.core, instancePath);
		expect(errors.value).toStrictEqual({
			value: "must be equal to one of the allowed values: a, b, c",
		});

		value.value = "a";

		expect(errors.value).toStrictEqual({ value: undefined });
	});
});
