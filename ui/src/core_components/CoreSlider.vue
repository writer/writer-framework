<template>
	<div class="CoreSlider component" :data-streamsync-id="componentId" v-show="!isPlaceholder">
        
        <div class="main">
            <div class="inputContainer">
                <input type="range" :min="min" :max="max" :value="value" v-on:change.prevent="handleChange($event)" />
            </div>
            
            <div class="rangeLabelContainer">
                <div class="min">{{ min }}</div>
                <div class="max">{{ max }}</div>
            </div>
        </div>

        <div class="label">
            <h2>{{ value }}</h2>
        </div>
    </div>
</template>

<script>
export default {
    inject: ["streamsync"],
    emit: ["change"],
    data: function () {
        return {
            value: 0
        }
    },
	props: {
        componentId: String
    },
    mounted: function () {
        this.streamsync.addEventListeners(this.componentId, this.$el);
    },
    methods: {
        handleChange: function (ev) {
            this.value = ev.target.value;
            this.$emit("change", ev);
        }
    },
    computed: {
        text: function () {
            return this.streamsync.getContentValue(this.componentId, "text");
        },
        min: function () {
            const v = this.streamsync.getContentValue(this.componentId, "min");
            if (v === null) return 0;
            return v;
        },
        max: function () {
            const v = this.streamsync.getContentValue(this.componentId, "max");
            if (v === null) return 0;
            return v;
        },
        isPlaceholder: function () {
            return this.streamsync.components[this.componentId].placeholder;
        }
    }
}
</script>

<style scoped>

.CoreSlider {
    display: flex;
    align-items: center;
}

.main {
    display: block;
    padding-top: 0.7rem;
    width: 30ch;
}

input {
    width: 100%;
    margin: 0;
}

.rangeLabelContainer {
    align-items: center;
    display: flex;
    justify-content: space-between;
    font-size: 0.7rem;
}

h2 {
    margin: 0;
}

.label {
    min-width: 32px;
    text-align: center;
    margin-left: 24px;
    padding: 16px;
    border-radius: 8px;
    background: var(--subtleHighlight);
}

</style>
