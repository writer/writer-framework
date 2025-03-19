<template>
	<BuilderSettingsProperties :group-level="0"></BuilderSettingsProperties>
	<BuilderSettingsActionSelect></BuilderSettingsActionSelect>
	<BuilderSettingsProperties :group-level="1"></BuilderSettingsProperties>
</template>

<script setup lang="ts">
import BuilderSettingsActionSelect from "@/builder/settings/BuilderSettingsActionSelect.vue";
import BuilderSettingsProperties from "@/builder/settings/BuilderSettingsProperties.vue";
</script>
