<!-- Wrapper page for all other pages -->
<template>
    <div class="min-h-screen">
        <header class="sticky top-0 h-14 flex items-center justify-between pl-2 pr-4 bg-main-200 z-30">
            <img
                class="h-12 p-2 cursor-pointer"
                src="/images/logo.svg"
                alt="logo"
                @click="$router.push('/')"
            />
            <user-component />
        </header>
        <router-view class="min-h-[calc(100vh-3.5rem)] h-full" />
        <message />
    </div>
</template>

<script lang="ts">
import UserComponent from "@/components/UserComponent.vue";
import Message from "@/components/ui/Message.vue";

export default {
    name: "App",
    components: {
        UserComponent,
        Message,
    },
}
</script>
