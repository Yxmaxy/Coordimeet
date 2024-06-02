<template>
    <div class="bg-main-000">
        <tab-controller :tabs="tabs" :breakpoint="750">
            <template v-slot:login>
                <div class="flex justify-center items-center h-full">
                    <form @submit.prevent="onLogin" class="flex flex-col">
                        <h1 class="text-4xl font-bold text-center text-main-700 mb-5">Log in</h1>

                        <custom-input
                            v-model="login.email"
                            type="email"
                            placeholder="Email"
                        />
                        <custom-input
                            v-model="login.password"
                            type="password"
                            placeholder="Password"
                        />

                        <custom-button
                            class="mt-2"
                        >
                            Log in
                        </custom-button>
                    </form>
                </div>
            </template>
            <template v-slot:signup>
                <div class="flex justify-center items-center h-full">
                    <form @submit.prevent="onSignup" class="flex flex-col">
                        <h1 class="text-4xl font-bold text-center text-main-700 mb-5">Sign up</h1>

                        <custom-input
                            v-model="signup.email"
                            type="email"
                            placeholder="Email"
                        />
                        <custom-input
                            v-model="signup.password"
                            type="password"
                            placeholder="Password"
                        />
                        <custom-input
                            v-model="signup.password2"
                            type="password"
                            placeholder="Repeat password"
                            invalidMessage="Passwords do not match"
                            :forceInvalidMessage="signup.password2.length > 0 && !passwordsMatch"
                        />

                        <custom-button
                            class="mt-2"
                            :disabled="!signup.email || !signup.password || !signup.password2 || !passwordsMatch"
                        >
                            Create an account
                        </custom-button>
                    </form>
                </div>
            </template>
        </tab-controller>
    </div>
</template>

<script lang="ts">
import { useStoreUser } from "@/stores/storeUser";

import { Tab } from "@/types/tabs";

import TabController from "@/components/TabController.vue";
import CustomInput from "@/components/ui/CustomInput.vue";
import CustomButton from "@/components/ui/CustomButton.vue";

const tabs = [
    {
        name: "Log in",
        slot_name: "login",
        icon: "login",
    },
    {
        name: "Sign up",
        slot_name: "signup",
        icon: "person_add",
    }
] as Tab[];

export default {
    name: "Login",
    components: {
        TabController,
        CustomInput,
        CustomButton,
    },
    setup() {
        const storeUser = useStoreUser();
        return {
            storeUser,
            tabs
        }
    },
    data() {
        return {
            checkPasswords: false,
            login: {
                email: "",
                password: "",
            },
            signup: {
                email: "",
                password: "",
                password2: "",
            },
        }
    },
    computed: {
        passwordsMatch(): boolean {
            return this.signup.password === this.signup.password2;
        }
    },
    methods: {
        async onLogin() {
            const successful = await this.storeUser.onLogin(this.login.email, this.login.password);
            if (successful) {
                const redirectLink = this.storeUser.redirectAfterLogin || "/event/list";
                this.$router.push(redirectLink);
            }
        },
        async onSignup() {
            if (!this.passwordsMatch) {
                return;
            }

            const successful = await this.storeUser.onSignup(this.signup.email, this.signup.password);
            if (successful) {
                const redirectLink = this.storeUser.redirectAfterLogin || "/event/list";
                this.$router.push(redirectLink);
            }
        }
    },
}
</script>
