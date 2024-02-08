<template>
    <div class="bg-main-000 flex justify-center items-center">
        <!-- <img class="pb-28" src="/images/logo.png" alt="CoordiMeet" /> -->

        <form @submit.prevent class="flex flex-col">
            <h1 class="text-4xl font-bold text-center text-main-700">Login</h1>
            <div class="text-center text-main-200 mb-4">(Temporary form)</div>

            <custom-input
                v-model="username"
                type="username"
                placeholder="Username"
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
            username: "",
            password: "",
        }
    },
    methods: {
        async onLogin() {
            const successful = await this.storeUser.onLogin(this.username, this.password);
            if (successful) {
                this.$router.push("/event/list");
            }
        }
    }
}
</script>
