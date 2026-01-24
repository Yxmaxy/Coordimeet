<template>
    <header class="sticky top-0 h-14 flex items-center justify-between pl-2 pr-4 bg-main-200 z-30">
        <img
            class="h-12 p-2 cursor-pointer"
            src="/images/logo.svg"
            alt="logo"
            @click="$router.push('/')"
        />
        <slot></slot>
    </header>
</template>

<script lang="ts">
export default {
    name: "AppHeader",
}
</script>
