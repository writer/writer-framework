function getPlatform() {
	const platform: string =
		navigator?.userAgentData?.platform || navigator?.platform;
	return platform;
}

export function getModifierKeyName() {
	return isPlatformMac() ? "⌘ Cmd" : "Ctrl";
}

export function isModifierKeyActive(ev: KeyboardEvent) {
	return isPlatformMac() ? ev.metaKey : ev.ctrlKey;
}

export function isPlatformMac() {
	const platform = getPlatform();
	if (platform.toLowerCase().indexOf("mac") != -1) return true;
	return false;
}
