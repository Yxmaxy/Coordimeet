<template>
    <div class="bg-main-000 flex justify-center items-center">
        <!-- <img class="pb-28" src="/images/logo.png" alt="CoordiMeet" /> -->

        <form @submit.prevent class="flex flex-col">
            <h1 class="text-4xl font-bold text-center text-main-700">Login</h1>
            <div class="text-center text-main-200 mb-4">(Temporary form)</div>

            <custom-input
                v-model="email"
                type="email"
                placeholder="Email"
            />
            <custom-input
                v-model="password"
                type="password"
                placeholder="Password"
            />

            <custom-button
                class="mt-4"
                :click="onLogin"
            >
                Log in
            </custom-button>
        </form>

        <custom-button
                class="mt-4"
                :click="notify"
        >
            Notify
        </custom-button>
    </div>
</template>

<script lang="ts">
import { useStoreUser } from "@/stores/storeUser";

import CustomInput from "@/components/ui/CustomInput.vue";
import CustomButton from "@/components/ui/CustomButton.vue";

export default {
    name: "Home",
    components: {
        CustomInput,
        CustomButton,
    },
    setup() {
        const storeUser = useStoreUser();
        return {
            storeUser,
        }
    },
    data() {
        return {
            email: "",
            password: "",
        }
    },
    methods: {
        async onLogin() {
            const successful = await this.storeUser.onLogin(this.email, this.password);
            if (successful) {
                this.$router.push("/event/list");
            }
        },
        async notify() {
            // Check if the browser supports notifications
            if (!("Notification" in window)) {
                console.log("This browser does not support desktop notification");
                alert("Not supported");
            }

            // Check whether notification permissions have already been granted
            else if (Notification.permission === "granted") {
                // If it's okay, let's create a notification
                var notification = new Notification("Hi there!");
            }

            // Otherwise, we need to ask the user for permission
            else if (Notification.permission !== "denied") {
                const permission = await Notification.requestPermission();
                    // If the user accepts, let's create a notification
                if (permission === "granted") {
                    var notification = new Notification("Hi there!");
                }
            } else {
                alert(Notification.permission)
            }
        }
    }
}
</script>
