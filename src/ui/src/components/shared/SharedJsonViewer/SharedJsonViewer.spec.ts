import { describe, expect, it } from "vitest";
import SharedJsonViewer from "./SharedJsonViewer.vue";
import SharedJsonViewerValue from "./SharedJsonViewerValue.vue";
import SharedJsonViewerObject from "./SharedJsonViewerObject.vue";
import { mount } from "@vue/test-utils";

describe("SharedJsonViewer", () => {
	it("should render a string", () => {
		const wrapper = mount(SharedJsonViewer, {
			propsData: { data: "string" },
		});
		const jsonValue = wrapper.getComponent(SharedJsonViewerValue);
		expect(jsonValue.text()).toBe('"string"');
	});

	it("should render a boolean", () => {
		const wrapper = mount(SharedJsonViewer, { propsData: { data: true } });
		const jsonValue = wrapper.getComponent(SharedJsonViewerValue);
		expect(jsonValue.text()).toBe("true");
	});

	it("should render a null", () => {
		const wrapper = mount(SharedJsonViewer, { propsData: { data: null } });
		const jsonValue = wrapper.getComponent(SharedJsonViewerValue);
		expect(jsonValue.text()).toBe("null");
	});

	it("should render an object", () => {
		const data = { a: "a", b: "b" };
		const wrapper = mount(SharedJsonViewer, { propsData: { data } });
		const jsonObject = wrapper.getComponent(SharedJsonViewerObject);
		expect(jsonObject.props().data).toStrictEqual(data);

		expect(wrapper.findAllComponents(SharedJsonViewerValue)).toHaveLength(
			2,
		);
	});

	it("should render a nested object", async () => {
		const data = { array: [1, 2, 3], nested: { foo: "bar", a: { b: 2 } } };
		const wrapper = mount(SharedJsonViewer, { propsData: { data } });

		expect(wrapper.element).toMatchSnapshot();
	});

	it("should render an array", async () => {
		const data = [1, 2, 3];
		const wrapper = mount(SharedJsonViewer, { propsData: { data } });

		expect(wrapper.element).toMatchSnapshot();
	});
});
