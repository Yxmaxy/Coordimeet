<template>
    <div
        :class="[{
            '!cursor-not-allowed opacity-75': disabled,
        }, 'cursor-pointer flex gap-1 items-center']"
    >
        <div @click="onToggle('left')">
            <slot name="left"></slot>
        </div>
        <div
            class="h-6 flex flex-col relative justify-center"
            @click="onToggle('toggle')"
        >
            <!-- Slider -->
            <div class="w-9 h-3 bg-main-300 rounded-full"></div>
            <!-- Circle -->
            <div :class="[{
                'left-0': !modelValue,
                'translate-x-4': modelValue,
            }, 'w-5 h-5 bg-main-400 rounded-full absolute transition-transform']"></div>
        </div>
        <div @click="onToggle('right')">
            <slot name="right"></slot>
        </div>
    </div>
</template>

<script lang="ts">
export default {
    name: "CustomToggle",
    emits: [ "update:modelValue" ],
    props: {
        modelValue: {
            type: Boolean,
            required: true
        },
        disabled: {
            type: Boolean,
            default: false,
        },
    },
    methods: {
        onToggle(direction: "left" | "right" | "toggle") {
            if (this.disabled)
                return;
            const conversion = {
                "left": false,
                "right": true,
                "toggle": !this.modelValue,
            }
            this.$emit("update:modelValue", conversion[direction])
        },
    },
}
</script>
