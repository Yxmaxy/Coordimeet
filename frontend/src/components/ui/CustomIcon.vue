<template>
    <span class="text-inherit material-symbols-outlined">{{ icon }}</span>
</template>

<script lang="ts">
export default {
    name: "CustomIcon",
    props: {
        icon: {
            type: String,
            required: true,
        },
    },
}
</script>
