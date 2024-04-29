<template>
    <div
        v-if="userStore.isLoggedIn"
        class="z-50 flex gap-2 relative"
    >
        <div
            @click="showLogout = !showLogout"
            class="h-full flex items-center cursor-pointer select-none"
        >
            <span class="material-symbols-outlined align-middle ml-1">menu</span>
        </div>
        <!-- Background -->
        <div
            v-if="showLogout"
            class="fixed left-0 right-0 top-0 bottom-0"
            @click="showLogout = false"
        ></div>
        <!-- Popup -->
        <template v-if="showLogout">
            <!-- Popup triangle -->
            <div class="absolute -bottom-2 right-1
                border-l-transparent border-t-transparent border-r-transparent border-b-main-400 border-8"></div>
            <!-- Content -->
            <div class="absolute w-screen top-7 -right-2 pl-4 pt-1 max-w-[20rem]">
                <div class="flex flex-col bg-main-300 border-2 border-main-400 rounded-lg [&>*]:py-3 [&>*]:px-4 shadow-md">
                    <button @click="onMenuClick('/event/list')" class="hover:bg-main-400 transition-colors flex items-center justify-between">
                        Events
                        <span class="material-symbols-outlined align-middle text-lg">calendar_today</span>
                    </button>
                    <button @click="onMenuClick('/group/list')" class="hover:bg-main-400 transition-colors flex items-center justify-between">
                        Groups
                        <span class="material-symbols-outlined align-middle text-lg">groups</span>
                    </button>
                    <button @click="onMenuClick('/')" class="hover:bg-main-400 transition-colors flex items-center justify-between">
                        My profile
                        <span class="material-symbols-outlined align-middle text-lg">person</span>
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
</template>

<script lang="ts">
import { useStoreUser } from "@/stores/storeUser";
import { setTheme, Theme } from "@/utils/theme";

import CustomButton from "@/components/ui/CustomButton.vue";

export default {
    name: "UserComponent",
    components: {
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
            showLogout: false,
            isMobile: true,
        }
    },
    computed: {
        userDisplayName() {
            if (this.userStore.user!.first_name && this.userStore.user!.last_name)
                return `${this.userStore.user!.first_name} ${this.userStore.user!.last_name}`;
            if (this.userStore.user!.first_name)
                return this.userStore.user!.first_name;
            return this.userStore.user!.email;
        }
    },
    methods: {
        setTheme,
        async onLogout() {
            await this.userStore.onLogout();
            this.showLogout = false;
            this.$router.push("/");
        },
        onMenuClick(path: string) {
            this.showLogout = false;
            this.$router.push(path);
        },
        checkScreenSize() {
            this.isMobile = window.innerWidth <= 400;
            window.innerWidth <= 400 ? this.isMobile = true : this.isMobile = false;
        },
    },
    mounted() {
        window.addEventListener('resize', this.checkScreenSize);
        this.$nextTick(() => {
            this.checkScreenSize();
        });
    },
    unmounted() {
        window.removeEventListener('resize', this.checkScreenSize);
    },
}
</script>
