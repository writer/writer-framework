import { ComponentPublicInstance, computed, Ref, ref, watch } from "vue";
import { useEvaluator } from "@/renderer/useEvaluator";
import { Core, InstancePath } from "@/writerTypes";
import { useComponentLinkedWorkflows } from "@/composables/useComponentWorkflows";

/**
 * Encapsulates repeatable form value logic, including binding.
 *
 * @param wf
 * @param componentId
 * @param defaultValue the initial value when binding is not set
 * @returns
 */
export function useFormValueBroker<T = any>(
	wf: Core,
	instancePath: InstancePath,
	emitterEl: Ref<HTMLElement | ComponentPublicInstance>,
	// @ts-expect-error keep default string for compatibility reason
	defaultValue: T = "",
) {
	const formValue: Ref<T> = ref();
	const isBusy = ref(false);
	const queuedEvent: Ref<{ eventValue: T; emitEventType: string }> =
		ref(null);

	const componentId = instancePath.at(-1).componentId;
	const component = computed(() => wf.getComponentById(componentId));
	const { evaluateExpression } = useEvaluator(wf);

	function initializeFormValueBroker() {
		const bindingEventType = component.value.binding?.eventType;
		if (!bindingEventType) return;
		handleInput(defaultValue, bindingEventType);
	}

	function getBindingValue() {
		const component = wf.getComponentById(componentId);
		if (component?.binding?.stateRef) {
			const value = evaluateExpression(
				component.binding.stateRef,
				instancePath,
			);
			return value;
		}
		return;
	}

	/**
	 * Takes a value and emits a CustomEvent of the given type.
	 * Deals with debouncing.
	 *
	 * @param newValue
	 * @param emitEventType
	 * @returns
	 */
	function handleInput(
		eventValue: any,
		emitEventType: string,
		customCallback?: Function,
	) {
		formValue.value = eventValue;

		const isHandlerSet = component.value.handlers?.[emitEventType];
		const isBindingSet =
			component.value.binding?.eventType == emitEventType;
		const isWorkflowAttached = useComponentLinkedWorkflows(
			wf,
			componentId,
			emitEventType,
		).isLinked.value;

		// Event is not used
		if (!isHandlerSet && !isBindingSet && !isWorkflowAttached) return;

		if (isBusy.value) {
			// Queued event is overwritten for debouncing purposes

			queuedEvent.value = {
				eventValue,
				emitEventType,
			};
			return;
		}

		isBusy.value = true;
		const callback = () => {
			isBusy.value = false;
			if (queuedEvent.value) {
				handleInput(
					queuedEvent.value.eventValue,
					queuedEvent.value.emitEventType,
				);
				queuedEvent.value = null;
			}
			customCallback?.();
		};

		const event = new CustomEvent(emitEventType, {
			detail: {
				payload: eventValue,
				callback,
			},
		});

		if (emitterEl.value instanceof HTMLElement) {
			emitterEl.value.dispatchEvent(event);
		} else {
			// Vue instance (ComponentPublicInstance)

			emitterEl.value.$el.dispatchEvent(event);
		}
	}

	watch(
		() => getBindingValue(),
		(value) => {
			if (isBusy.value) return;
			formValue.value = value as T;
		},
		{ immediate: true },
	);

	watch(
		formValue,
		(newValue) => {
			if (typeof newValue === "undefined") {
				formValue.value = defaultValue;
			}
		},
		{ immediate: true },
	);

	return {
		formValue,
		handleInput,
		initializeFormValueBroker
	};
}
