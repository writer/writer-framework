<script lang="ts">
import { computed, h, inject, provide, ref, watch } from "vue";
import templateMap from "../core/templateMap";
import { Component, InstancePath, InstancePathItem } from "../streamsyncTypes";
import ComponentProxy from "./ComponentProxy.vue";
import { useTemplateEvaluator } from "./useTemplateEvaluator";
import injectionKeys from "../injectionKeys";
import { VNode } from "vue";
import ChildlessPlaceholder from "./ChildlessPlaceholder.vue";

const fallbackRender = (type: string) => () =>
	h("div", `Component type ${type} not supported.`);

export default {
	props: ["componentId", "instancePath", "instanceData"],
	setup(props) {
		const ss = inject(injectionKeys.core);
		const ssbm = inject(injectionKeys.builderManager);
		const componentId: Component["id"] = props.componentId;
		const component = computed(() => ss.getComponentById(componentId));
		const template = templateMap[component.value.type];
		if (!template) {
			return fallbackRender(component.value.type);
		}
		const instancePath: InstancePath = props.instancePath;
		const instanceData = props.instanceData;
		const { getEvaluatedFields, isComponentVisible } = useTemplateEvaluator(ss);
		const evaluatedFields = getEvaluatedFields(instancePath);

		const children = computed(() => ss.getComponents(componentId, true));
		const isBeingEdited = computed(
			() => !!ssbm && ssbm.getMode() != "preview"
		);

		const getChildlessPlaceholderVNode = (): VNode => {
			if (children.value.length > 0) return;
			return h(ChildlessPlaceholder, {
				componentId: component.value.id,
			});
		};

		const renderProxiedComponent = (
			componentId: Component["id"],
			instanceNumber: InstancePathItem["instanceNumber"] = 0
		) => {
			const vnode = h(ComponentProxy, {
				componentId,
				key: `${componentId}:${instanceNumber}`,
				instancePath: [
					...instancePath,
					{
						componentId: componentId,
						instanceNumber,
					},
				],
				instanceData: [...instanceData, ref(null)],
			});
			return vnode;
		};

		const getChildrenVNodes = (
			instanceNumber: InstancePathItem["instanceNumber"] = 0,
			componentFilter: (c: Component) => boolean = () => true,
			positionlessSlot: boolean = false
		): VNode[] => {
			const renderInsertionSlot = (position: number) => {
				return h("div", {
					"data-streamsync-slot-of-id": componentId,
					"data-streamsync-position": position,
				});
			};
			const showSlots = isBeingEdited.value && !positionlessSlot;

			const childrenVNodes = children.value
				.filter(componentFilter)
				.map((childComponent, childIndex) => {
					const childVNode = renderProxiedComponent(
						childComponent.id,
						instanceNumber
					);
					return [
						childVNode,
						...(showSlots
							? [renderInsertionSlot(childIndex + 1)]
							: []),
					];
				});

			return [...(showSlots ? [renderInsertionSlot(0)] : [])].concat(
				childrenVNodes.flat()
			);
		};

		provide(injectionKeys.evaluatedFields, evaluatedFields);
		provide(injectionKeys.componentId, componentId);
		provide(injectionKeys.isBeingEdited, isBeingEdited);
		provide(injectionKeys.instancePath, instancePath);
		provide(injectionKeys.instanceData, instanceData);
		provide(injectionKeys.renderProxiedComponent, renderProxiedComponent);
		provide(injectionKeys.getChildrenVNodes, getChildrenVNodes);

		const flattenInstancePath = (path: InstancePath) => {
			return path
				.map((ie) => `${ie.componentId}:${ie.instanceNumber}`)
				.join(",");
		};

		const dataAttrs = {
			"data-streamsync-id": componentId,
			"data-streamsync-instance-path": flattenInstancePath(instancePath),
		};

		/*
		Selected stylesheet class is removed if changes are made,
		for the developer to appreciate the changes. Particularly important
		for colour changes, with which selection interferes.
		*/

		const isSelected = ref(false);
		watch(
			() => ssbm?.getSelectedId() == componentId,
			(isNowSelected) => {
				isSelected.value = isNowSelected;
			}
		);
		watch(() => evaluatedFields, () => {
			isSelected.value = false;
		}, {deep: true});

		const isChildless = computed(() => children.value.length == 0);
		const isVisible = computed(() => isComponentVisible(componentId, instancePath));

		const getHandlerCallable = (handlerFunction: string) => {
			const isForwardable = !handlerFunction.startsWith("$");
			if (isForwardable) {
				return (ev: Event) => ss.forwardEvent(ev, instancePath);
			}
			if (handlerFunction.startsWith("$goToPage_")) {
				const pageKey = handlerFunction.substring("$goToPage_".length);
				return (ev: Event) => ss.setActivePageFromKey(pageKey);
			}
			return null;
		};

		const eventHandlerProps = computed(() => {
			const props = {};

			// Binding. Make sure there's a handler to catch the binding event.
			// Might be overwritten by a handler

			if (component.value.binding) {
				const bindingEventType = component.value.binding.eventType;
				const eventKey = `on${bindingEventType
					.charAt(0)
					.toUpperCase()}${bindingEventType.slice(1)}`;
				props[eventKey] = (ev: Event) =>
					ss.forwardEvent(ev, instancePath);
			}

			// Handle event handlers

			Object.entries(component.value.handlers ?? {}).forEach(
				([handlerEventType, handlerFunction]) => {
					const eventKey = `on${handlerEventType
						.charAt(0)
						.toUpperCase()}${handlerEventType.slice(1)}`;
					props[eventKey] = getHandlerCallable(handlerFunction);
				}
			);
			return props;
		});

		const fieldBasedStyleVars = computed(() => {
			const fields = ss.getComponentDefinition(
				component.value.type
			)?.fields;
			if (!fields) return;
			const styleVars = {};
			Object.keys(fields).forEach((key) => {
				if (!fields[key].applyStyleVariable) return;
				if (!evaluatedFields[key]) return;
				styleVars[`--${key}`] = evaluatedFields[key].value;
			});
			return styleVars;
		});

		const getRootElProps = function () {
			const rootElProps = {
				class: {
					component: true,
					childless: isChildless.value,
					selected: isSelected.value,
				},
				style: {
					...fieldBasedStyleVars.value,
					...(!isVisible.value ? { display: "none" } : {}),
				},
				...dataAttrs,
				...eventHandlerProps.value,
				draggable: isBeingEdited.value,
			};
			return rootElProps;
		};

		return () => {
			const childlessPlaceholder = isBeingEdited.value
				? getChildlessPlaceholderVNode()
				: undefined;

			const defaultSlotFn = ({
				instanceNumber = 0,
				componentFilter = () => true,
				positionlessSlot = false,
			}: {
				instanceNumber: number;
				componentFilter: (c: Component) => boolean;
				positionlessSlot: boolean;
			}) => {
				if (isChildless.value) {
					return positionlessSlot ? undefined : childlessPlaceholder;
				}
				const vnodes = getChildrenVNodes(
					instanceNumber,
					componentFilter,
					positionlessSlot
				);
				return vnodes;
			};

			const vnodeProps = {
				...getRootElProps(),
			};
			const renderedComponent = h(template, vnodeProps, {
				default: defaultSlotFn,
			});

			return renderedComponent;
		};
	},
};
</script>
<style scoped>
@import "../renderer/sharedStyles.css";
</style>
