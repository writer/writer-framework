<!-- <script setup>
    import { generateCore } from "../../../ui/src/core"
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
    
    function getEventsWithoutStub() {
        const ews = [];
        defs.filter(d => d.events).forEach(d =>
            Object.entries(d.events).forEach(([eId, e]) => {
                ews.push({ componentType: d.type, eventType: eId, missingStub: !e.stub });
            })
        );
        return ews;
    }

</script>

# Internal docs

This list is automatically generated to help Streamsync contributors. It's likely not useful for end users.

## Component overview

Component count: {{ Object.keys(defs).length }}

<ul>
    <li v-for="def in defs">{{def.name}} ({{ def.type }})</li>
</ul>

## Events without stubs

<table>
    <thead>
        <tr>
            <th>Component type</th>
            <th>Event type</th>
            <th>Missing stub</th>
        </tr>
    </thead>
    <tbody>
        <tr v-for="item in getEventsWithoutStub()">
            <td>{{ item.componentType }}</td>
            <td>{{ item.eventType }}</td>
            <td>{{ item.missingStub ? "Yes" : "" }}</td>
        </tr>
    </tbody>
</table> -->
