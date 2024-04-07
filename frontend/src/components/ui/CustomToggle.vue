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
                'left-0': !isRight,
                'translate-x-4': isRight,
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
            type: [String, Number, Boolean],
            required: true
        },
        disabled: {
            type: Boolean,
            default: false,
        },
        leftValue: {
            type: [String, Number, Boolean],
            default: false,
        },
        rightValue: {
            type: [String, Number, Boolean],
            default: true,
        },
    },
    computed: {
        isRight() {
            return this.modelValue === this.rightValue;
        },
    },
    methods: {
        onToggle(direction: "left" | "right" | "toggle") {
            if (this.disabled)
                return;
            
            if (direction === "left")
                this.$emit("update:modelValue", this.leftValue);
            else if (direction === "right")
                this.$emit("update:modelValue", this.rightValue);
            else {
                this.$emit("update:modelValue", this.isRight ? this.leftValue : this.rightValue);
            }

        },
    },
}
</script>
