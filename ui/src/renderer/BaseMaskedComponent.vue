<template>
	<div class="BaseMaskedComponent">
		<slot />
		<div class="mask" />
	</div>
</template>

<style scoped>
.BaseMaskedComponent {
	position: relative;
}
.BaseMaskedComponent .mask {
	pointer-events: none;
}

.BaseMaskedComponent.beingEdited .mask {
	pointer-events: auto;
	position: absolute;
	top: 0;
	left: 0;
	width: 100%;
	height: 100%;
}

.BaseMaskedComponent.beingEdited.selected .mask {
	pointer-events: none;
}
</style>
