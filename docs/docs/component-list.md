---
outline: [2, 2]
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

<div v-for="categoryDesc, categoryKey in categories" class="componentCategory">
    <h2 :id="categoryKey">{{categoryKey}}</h2>
    {{ categoryDesc}}
    <div class="boxContainer">
        <div v-for="def in defs.filter(d => d.category == categoryKey)" class="box">
            <h3 :id="def.type">{{def.name}}</h3>
            <div class="imageContainer">
                <div class="imageContainerInner">
                    <img :src="`/components/${def.type}.png`" />
                </div>
            </div>
            <div class="descriptionContainer">
                {{def.description}}
                <details v-if="def.fields">
                    <summary>Fields</summary>
                    <ul>
                        <li v-for="[fieldId, field] in Object.entries(def.fields)">
                            {{ field.name }}
                            <span class="secondaryText">: {{ field.type }}</span>
                            <span v-if="field.options" class="secondaryText"> &middot; {{ Object.values(field.options ?? {}).join(" / ") }}</span>
                            <template v-if="field.desc"> &middot; {{ field.desc }}</template>
                        </li>
                    </ul>
                </details>
                <details v-if="def.events">
                    <summary>Events</summary>
                    <ul>
                        <li v-for="[eventId, event] in Object.entries(def.events)">
                            <code>{{ eventId }}</code> <template v-if="event.desc">&middot; {{ event.desc }}</template>
                        </li>
                    </ul>
                </details>
            </div>
        </div>
    </div>
</div>

<style>

.componentCategory .secondaryText {
    color: #909090;
}

.componentCategory .boxContainer {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
    gap: 16px;
    margin-top: 16px;
}

.componentCategory .box {
    border: 1px solid var(--vp-c-divider);
    border-radius: 8px;
}

.componentCategory .box h3 {
    margin: 16px;
    font-size: 1rem;
    font-weight: normal;
}

.componentCategory .box .imageContainer {
    background: #E9EEF1;
    border-top: 1px solid #E9EEF1;
    border-bottom: 1px solid #E9EEF1;
    width: 100%;
    height: 160px;
    overflow: hidden;
    padding: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
}

.componentCategory .box .imageContainerInner {
    display: flex;
    align-items: flex-start;
    max-height: 144px;
}

.componentCategory .box img {
    max-height: 144px;
}

.componentCategory .box summary {
    margin-bottom: 0;
}

.componentCategory .box .descriptionContainer {
    padding: 16px;
}

</style>
