<!-- Wrapper page for all other pages -->
<template>
    <div class="min-h-screen">
        <router-view class="min-h-[calc(100vh-3.5rem)] h-full" />
        <message />
    </div>
</template>

<script lang="ts">
import Message from "@/components/ui/Message.vue";

export default {
    name: "App",
    components: {
        Message,
    },
}
</script>
