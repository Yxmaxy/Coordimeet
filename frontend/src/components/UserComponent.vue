<template>
    <a 
        v-if="!userStore.isLoggedIn"
        class="btn"
        :href="loginLink"
    >Log in</a>
    <div
        v-if="userStore.isLoggedIn && !showLogout"
        class="profile"
        @click="showLogout = true"
    >
        <div>
            {{ userStore.user.FirstName }}
        </div>
        <img
            :src="userStore.user.ProfilePhoto"
            alt="profile"
            referrerpolicy="no-referrer"
        />
    </div>
    <button 
        v-if="userStore.isLoggedIn && showLogout"
        :href="loginLink"
        @click="logout"
    >Log out</button>
</template>

<script lang="ts">
import axios from 'axios'
import { IUser } from '../common/interfaces';
import { useUserStore } from '../common/stores/UserStore'

export default {
    setup() {
        const userStore = useUserStore();
        return {
            userStore,
        }
    },
    data() {
        return {
            loginLink: "",
            showLogout: false,
        }
    },
    methods: {
        getLoginData() {
            axios.get("https://coordimeet.eu/backend/googleLogin.php")
            .then(res => {
                if ("googleLoginURL" in res.data)
                    this.loginLink = res.data.googleLoginURL;
                else {
                    console.log(res.data);
                    
                    this.userStore.isLoggedIn = true;
                    this.userStore.user = res.data;
                    this.$router.push("/event/list");
                }
            })
        },
        logout() {
            this.userStore.isLoggedIn = false;
            this.userStore.user = {} as IUser;
            this.$router.push("/");
            // TODO add backend logout
        },
    },
    mounted() {
        this.getLoginData();
    }
}
</script>

<style lang="scss">
@import "../styles/colors.scss";

.profile {
    display: flex;
    flex-direction: row;
    align-items: center;
    height: 150%;
    gap: 8px;
    user-select: none;
    cursor: pointer;
    & > div {
        font-weight: bold;
    }
    img {
        height: 100%;
        border: {
            radius: 100%;
        }
    }
}
</style>