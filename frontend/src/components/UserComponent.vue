<template>
    <div
        v-if="isLoggedIn"
        class="z-50 flex gap-2 relative"
    >
        <div
            tabindex="0"
            @click="showPopup = !showPopup"
            @keydown.enter="showPopup = !showPopup"
            class="h-full flex items-center cursor-pointer select-none"
        >
            <span class="material-symbols-outlined align-middle ml-1">menu</span>
        </div>
        <!-- Background -->
        <div
            v-if="showPopup"
            class="fixed left-0 right-0 top-0 bottom-0"
            @click="showPopup = false"
        ></div>
        <!-- Popup -->
        <template v-if="showPopup">
            <!-- Popup triangle -->
            <div class="absolute -bottom-2 right-1
                border-l-transparent border-t-transparent border-r-transparent border-b-main-400 border-8"></div>
            <!-- Content -->
            <div class="absolute w-screen top-7 -right-2 pl-4 pt-1 max-w-[20rem]">
                <div class="flex flex-col bg-main-300 border-2 border-main-400 rounded-lg [&>*]:py-3 [&>*]:px-4 shadow-md">
                    <div class="flex items-center justify-between">
                        {{ userDisplayName }}
                        <span class="material-symbols-outlined align-middle text-lg">person</span>
                    </div>
                    <router-link to="/event/list" @click="closePopup" class="hover:bg-main-400 transition-colors flex items-center justify-between">
                        Events
                        <span class="material-symbols-outlined align-middle text-lg">calendar_today</span>
                    </router-link>
                    <router-link to="/group/list" @click="closePopup" class="hover:bg-main-400 transition-colors flex items-center justify-between">
                        Groups
                        <span class="material-symbols-outlined align-middle text-lg">groups</span>
                    </router-link>
                    <!-- <router-link to="/" @click="closePopup" class="hover:bg-main-400 transition-colors flex items-center justify-between">
                        My profile
                        <span class="material-symbols-outlined align-middle text-lg">person</span>
                    </router-link> -->
                    <button @click="onInstall" class="hover:bg-main-400 transition-colors flex items-center justify-between">
                        Install app
                        <span class="material-symbols-outlined align-middle text-lg">download</span>
                    </button>
                    <button @click="onLogout" class="hover:bg-main-400 transition-colors flex items-center justify-between">
                        Log out
                        <span class="material-symbols-outlined align-middle text-lg">logout</span>
                    </button>
                    <div class="flex items-center justify-between">
                        Theme
                        <div class="flex gap-1 [&>*]:h-5 [&>*]:w-5 [&>*]:rounded-sm [&>*]:border-2 [&>*]:border-main-600 [&>*]:cursor-pointer">
                            <div
                                @click="setTheme(Theme.BLUE)"
                                class="bg-[#41b9d6]"
                            ></div>
                            <div
                                @click="setTheme(Theme.GREEN)"
                                class="bg-[#41D6A9]"
                            ></div>
                            <div
                                @click="setTheme(Theme.PINK)"
                                class="bg-[#e178cd]"
                            ></div>
                            <div
                                @click="setTheme(Theme.DARK)"
                                class="bg-[#2a393f]"
                            ></div>
                        </div>
                    </div>
                </div>
            </div>
        </template>
    </div>
    <!-- <router-link
        v-else
        to="/login"
        class="h-full flex items-center cursor-pointer select-none"
    >
        <span class="material-symbols-outlined align-middle ml-1">login</span>
    </router-link> -->
</template>

<script lang="ts">
import { RouterLink } from "vue-router";
import { useStoreUser } from "@/stores/storeUser";
import { setTheme, Theme } from "@/utils/theme";

import CustomButton from "@/components/ui/CustomButton.vue";

export default {
    name: "UserComponent",
    components: {
        RouterLink,
        CustomButton,
    },
    setup() {
        const userStore = useStoreUser();
        return {
            userStore,
            Theme,
        }
    },
    data() {
        return {
            showPopup: false,
            isMobile: true,
            isLoggedIn: false,
            deferredInstallPrompt: null as any,
        }
    },
    computed: {
        userDisplayName() {
            return this.userStore.user!.email;
        }
    },
    methods: {
        setTheme,
        async onLogout() {
            await this.userStore.onLogout();
            this.showPopup = false;
            this.$router.push("/");
            this.isLoggedIn = false;
        },
        onMenuClick(path: string) {
            this.showPopup = false;
            this.$router.push(path);
        },
        closePopup() {
            this.showPopup = false;
        },
        checkScreenSize() {
            this.isMobile = window.innerWidth <= 400;
            window.innerWidth <= 400 ? this.isMobile = true : this.isMobile = false;
        },
        onInstall() {
            if (this.deferredInstallPrompt) {
                this.deferredInstallPrompt.prompt();
                this.deferredInstallPrompt.userChoice.then((choiceResult: any) => {
                    this.deferredInstallPrompt = null;
                });
            }
        },
        handleInstallPrompt(event: Event) {
            event.preventDefault();
            this.deferredInstallPrompt = event;
        },
    },
    async mounted() {
        window.addEventListener("resize", this.checkScreenSize);
        this.$nextTick(() => {
            this.checkScreenSize();
        });
        this.isLoggedIn = await this.userStore.isLoggedIn();

        window.addEventListener("beforeinstallprompt", this.handleInstallPrompt);
    },
    unmounted() {
        window.removeEventListener("resize", this.checkScreenSize);
        window.removeEventListener("beforeinstallprompt", this.handleInstallPrompt);
    },
    watch: {
        "userStore.user"(n) {
            this.isLoggedIn = !!n;
        }
    },
}
</script>
