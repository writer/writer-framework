<template>
	<div class="ComponentBase">
		<slot />
		<div class="mask" />
	</div>
</template>

<style scoped>
.ComponentBase .mask {
	pointer-events: none;
}

.ComponentBase.beingEdited .mask {
	pointer-events: auto;
	position: absolute;
	top: 0;
	left: 0;
	width: 100%;
	height: 100%;
}

.ComponentBase.beingEdited.selected .mask {
	pointer-events: none;
}
</style>
