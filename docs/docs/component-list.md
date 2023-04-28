---
outline: [2, 3]
---

<script setup>
    import { generateCore } from "../../ui/src/core"
    const ss = generateCore();
    const types = ss.getSupportedComponentTypes();
    const defs = types.map(type => {
        const def = ss.getComponentDefinition(type);
        return {
            type,
            name: def.name,
            docs: def.docs,
            description: def.description,
            fields: def.fields,
            events: def.events,
            category: def.category
        }
    });
    const categories = {
        "Layout": "Components to organise the app's layout. Not meaningful by themselves; their objective is to enhance how other components are presented.",
        "Content": "Components that present content and are meaningful by themselves. For example, charts, images or text.",
        "Input": "Components whose main objective is to allow the user to input data into the app.",
        "Other": "These components occupy a special role and are amongst the most powerful in the framework.",
        "Root": "These components are the top-level containers."
    };
     
</script>

# Component list

This list is automatically generated from the framework's source code.

::: tip Streamsync Builder displays this data in-context, when selecting a component.
This page mainly intended towards those exploring the framework before installing it.
:::

<div v-for="categoryDesc, categoryKey in categories">
<h2 :id="categoryKey">{{categoryKey}}</h2>
{{ categoryDesc}}
<div v-for="def in defs.filter(d => d.category == categoryKey)">
<h3 :id="def.type">{{def.name}}</h3><br />
{{def.description}}

<div v-if="def.fields">
<br />
Fields:

<ul>
<li v-for="[fieldId, field] in Object.entries(def.fields)">
{{ field.name }}
<span class="secondaryText">: {{ field.type }}
</span>
<span v-if="field.options" class="secondaryText"> &middot; {{ Object.values(field.options ?? {}).join(" / ") }}</span>
<template v-if="field.desc"> &middot; {{ field.desc }}</template>
</li>
</ul>
</div>

<div v-if="def.events">
<br />
Events:

<ul>
<li v-for="[eventId, event] in Object.entries(def.events)">
<code>{{ eventId }}</code> <template v-if="event.desc">&middot; {{ event.desc }}</template>
</li>
</ul>
</div>
</div>

</div>

<style>

.secondaryText {
    color: #909090;
}

</style>
