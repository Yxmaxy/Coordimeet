<template>
    <div
        class="flex items-center cursor-pointer select-none gap-2"
        @click="$emit('update:modelValue', value)"
    >
        <div
            class="w-4 h-4 flex justify-center items-center
                bg-white border-main-500 border-2 rounded-full">
            <div v-if="modelValue === value"
                class="w-2 h-2 rounded-full bg-main-500"
            ></div>
        </div>
        {{ text }}
    </div>
</template>

<script lang="ts">
export default {
    name: "CustomRadio",
    emits: [
        "update:modelValue"
    ],
    props: {
        modelValue: {
            type: [String, Number],
            required: true,
        },
        value: {
            type: [String, Number],
            required: true,
        },
        text: {
            type: String,
            default: "",
        }
    }
}
</script>
