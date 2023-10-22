<template>
    <button class="text-white bg-main-400 transition-colors
        hover:text-main-100 hover:bg-main-500
        active:text-main-200 active: active:bg-main-600
        font-bold rounded-lg py-1.5 px-2.5 select-none">
        <slot></slot>
    </button>
</template>

<script lang="ts">
export default {
    name: "CustomButton",
}
</script>
