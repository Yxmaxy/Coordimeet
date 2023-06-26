<template>
    <div class="h-full">
        <div class="relative h-full">
            <div
                class="h-full"
                @click="$emit('update:show', !show)"
            >
                <slot name="initiator"></slot>
            </div>
            <div class="absolute left-0 bg-red-500 w-full">
                <slot name="content" v-if="show"></slot>
            </div>
        </div>
    </div>
    <div
        
        class="relative"
    >
    </div>
</template>

<script lang="ts">
export default {
    name: "Popup",
    props: {
        show: Boolean,
    },
    emits: ["update:show"],
}
</script>
