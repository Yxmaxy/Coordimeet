<!-- Wrapper page for all other pages -->
<template>
    <div class="min-h-screen">
        <header class="sticky top-0 h-14 flex items-center justify-between pl-2 pr-4 bg-main-200 z-30">
            <img
                class="h-full p-2 cursor-pointer"
                src="/images/logo.png"
                alt="logo"
                @click="$router.push('/')"
            />
            <user-component />
        </header>
        <router-view class="min-h-[calc(100vh-3.5rem)] h-full" />
    </div>
    <footer class="h-14 flex items-center pl-4 pr-4 bg-main-200">
        <div>
            &copy; 2023
            <a href="https://vrecer.si">
                Marko,
            </a>
            <a href="https://leepush.eu">
                Bine,
            </a>
            <a href="https://nikigre.si">
                Nik,
            </a>
            <span>
                Nika,
            </span>
            <span>
                Rok.
            </span>
        </div>
    </footer>
</template>

<script lang="ts">
import UserComponent from "@/components/UserComponent.vue";

export default {
    name: "App",
    components: {
        "user-component": UserComponent,
    }
}
</script>
