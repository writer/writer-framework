/**
 * @param ev event from a mouse click, or a keyboard click (using tab navigation, then click with `Enter`)
 */
export function getClick(ev: MouseEvent | KeyboardEvent): CustomEvent {
	const payload = {
		ctrlKey: ev.ctrlKey,
		shiftKey: ev.shiftKey,
		metaKey: ev.metaKey,
	};
	const event = new CustomEvent("wf-click", {
		detail: {
			payload,
		},
	});
	return event;
}

export function getKeydown(ev: KeyboardEvent): CustomEvent {
	const payload = {
		key: ev.key,
		ctrlKey: ev.ctrlKey,
		shiftKey: ev.shiftKey,
		metaKey: ev.metaKey,
	};
	const event = new CustomEvent("wf-keydown", {
		detail: {
			payload,
		},
	});
	return event;
}
