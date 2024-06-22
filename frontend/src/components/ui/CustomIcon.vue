<template>
    <abbr
        v-if="title"
        class="text-inherit flex no-underline" :title="title"
    >
        <span class="text-inherit material-symbols-outlined">{{ icon }}</span>
    </abbr>
    <span v-else class="text-inherit material-symbols-outlined">{{ icon }}</span>
</template>

<script lang="ts">
export default {
    name: "CustomIcon",
    props: {
        title: {
            type: String,
            required: false,
        },
        icon: {
            type: String,
            required: true,
        },
    },
}
</script>
