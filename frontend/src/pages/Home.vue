<template>
    <div>
        <app-header>
            <div class="flex gap-2">
                <custom-button :small="true" :click="onLogin">
                    Log in
                </custom-button>
                <custom-button :small="true" :click="onAnonymousLogin">
                    Anonymous log in
                </custom-button>
            </div>
        </app-header>
        <div class="bg-main-000 flex justify-center items-center flex-col min-h-[calc(100vh-3.5rem)]">
            <h1 class="text-4xl font-bold text-center text-main-700 mb-5">Welcome to Coordimeet</h1>
            <p class="text-center text-main-500">Organise events with your friends and select the date when you are available.</p>
        </div>
    </div>
</template>

<script lang="ts">
import AppHeader from "@/components/AppHeader.vue";
import CustomButton from "@/components/ui/CustomButton.vue";

export default {
    name: "Home",
    components: {
        AppHeader,
        CustomButton,
    },
    methods: {
        onLogin() {
            window.location.href = import.meta.env.VITE_LOGIN_URL;
        },
        onAnonymousLogin() {
            this.$router.push({ name: "event_list" });
        },
    },
}
</script>
