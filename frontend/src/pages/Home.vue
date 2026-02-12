<template>
    <div v-if="loading" class="flex justify-center items-center h-screen">
        <div class="text-2xl font-bold">
            <custom-icon icon="progress_activity" class="text-4xl animate-spin text-main-400" />
        </div>
    </div>
    <div v-else class="min-h-screen bg-gradient-to-br from-main-000 via-main-50 to-main-100">
        <app-header>
            <div class="flex gap-2">
                <custom-button :small="true" :click="onLogin">
                    Log in
                </custom-button>
            </div>
        </app-header>
        
        <!-- Hero Section -->
        <div class="container mx-auto px-4 py-16 md:py-24">
            <div class="text-center max-w-4xl mx-auto">
                <h1 class="text-4xl md:text-5xl font-bold text-main-900 mt-5 mb-6 leading-tight animate-fade-in">
                    Coordinating Your Events, Has
                    <span class="text-main-600">
                        Never Been Easier
                    </span>
                </h1>
                <p class="text-lg md:text-xl text-main-600 mb-8 mt-8 leading-relaxed">
                    Organize events with friends and stay updated on every change. 
                    Never miss a beat when plans evolve.
                </p>
                
                <!-- Visual Element -->
                <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mt-20">
                    <!-- Smart Scheduling Card -->
                    <div class="relative group">
                        <div class="absolute inset-0 bg-gradient-to-r from-main-400 to-main-600 rounded-2xl blur-xl opacity-20 group-hover:opacity-30 transition-opacity"></div>
                        <div class="relative bg-white/80 backdrop-blur-sm rounded-2xl shadow-xl p-8 border border-main-200 text-center">
                            <div class="text-main-600 mb-4 flex justify-center">
                                <custom-icon icon="calendar_month" class="text-5xl" />
                            </div>
                            <h3 class="text-lg font-semibold text-main-800 mb-2">Smart Scheduling</h3>
                            <p class="text-main-600 text-sm">Find the perfect time that works for everyone</p>
                        </div>
                    </div>

                    <!-- Instant Updates Card -->
                    <div class="relative group">
                        <div class="absolute inset-0 bg-gradient-to-r from-main-400 to-main-600 rounded-2xl blur-xl opacity-20 group-hover:opacity-30 transition-opacity"></div>
                        <div class="relative bg-white/80 backdrop-blur-sm rounded-2xl shadow-xl p-8 border border-main-200 text-center">
                            <div class="text-main-600 mb-4 flex justify-center">
                                <custom-icon icon="notifications_active" class="text-5xl" />
                            </div>
                            <h3 class="text-lg font-semibold text-main-800 mb-2">Instant Updates</h3>
                            <p class="text-main-600 text-sm">Get notified immediately when event details change</p>
                        </div>
                    </div>

                    <!-- Easy Collaboration Card -->
                    <div class="relative group">
                        <div class="absolute inset-0 bg-gradient-to-r from-main-400 to-main-600 rounded-2xl blur-xl opacity-20 group-hover:opacity-30 transition-opacity"></div>
                        <div class="relative bg-white/80 backdrop-blur-sm rounded-2xl shadow-xl p-8 border border-main-200 text-center">
                            <div class="text-main-600 mb-4 flex justify-center">
                                <custom-icon icon="groups" class="text-5xl" />
                            </div>
                            <h3 class="text-lg font-semibold text-main-800 mb-2">Easy Collaboration</h3>
                            <p class="text-main-600 text-sm">Coordinate seamlessly with your entire group</p>
                        </div>
                    </div>
                </div>

            </div>
        </div>
    </div>
</template>

<script lang="ts">
import { useStoreUser } from "@/stores/storeUser";

import AppHeader from "@/components/AppHeader.vue";
import CustomButton from "@/components/ui/CustomButton.vue";
import CustomIcon from "@/components/ui/CustomIcon.vue";

export default {
    name: "Home",
    components: {
        AppHeader,
        CustomButton,
        CustomIcon,
    },
    setup() {
        const storeUser = useStoreUser();
        return {
            storeUser,
        }
    },
    data() {
        return {
            loading: true,
        }
    },
    async mounted() {
        const isLoggedIn = await this.storeUser.checkIfLoggedIn();
        if (isLoggedIn) {
            this.$router.push({ name: "event_list" });
        }
        this.loading = false;
    },
    methods: {
        onLogin() {
            window.location.href = import.meta.env.VITE_LOGIN_URL;
        },
    },
}
</script>
