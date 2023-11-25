<template>
    <button
        @click.stop="if (!disabled && click) click();"
        :class="[
            'text-white bg-main-400 transition-colors',
            'hover:text-main-100 hover:bg-main-500',
            'active:text-main-200 active: active:bg-main-600',
            'font-bold rounded-lg py-1.5 px-2.5 select-none',
            {
                'text-sm py-1 px-2': small,
                'bg-calendar-unavailable': negative,
                'bg-main-100 cursor-not-allowed active:text-main-300 active:bg-main-400': disabled,
            },
        ]"
    >
        <slot></slot>
    </button>
</template>

<script lang="ts">
export default {
    name: "CustomButton",
    props: {
        small: {
            type: Boolean,
            default: false,
        },
        disabled: {
            type: Boolean,
            default: false,
        },
        negative: {
            type: Boolean,
            default: false,
        },
        click: {
            type: Function,
            default: null,
        },
    }
}
</script>
