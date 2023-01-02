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
    <a 
        v-if="userStore.isLoggedIn && showLogout"
        class="btn"
        :href="logoutLink"
    >Log out</a>
</template>

<script lang="ts">
import axios from 'axios'
import { apiServer } from '../common/globals';
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
            logoutLink: `${apiServer}/googleLogout.php`,
            loginLink: "",
            showLogout: false,
        }
    },
    methods: {
        getLoginData() {
            axios.get(`${apiServer}/googleLogin.php`)
            .then(res => {
                if ("googleLoginURL" in res.data)
                    this.loginLink = res.data.googleLoginURL;
                else {
                    this.userStore.isLoggedIn = true;
                    this.userStore.user = res.data;
                }
            })
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
    height: 90%;
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