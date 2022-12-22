<!-- Header on top of the page -->
<template>
    <header class="header-component">
        <img src="/images/logo.png" alt="logo" @click="$router.push('/')"/>
        <div>
            <a class="btn" :href="loginLink">Log in</a>
        </div>
    </header>
</template>

<script lang="ts">
import axios from 'axios'

export default {
    data() {
        return {
            loginLink: ""
        }
    },
    methods: {
        getLoginData() {
            axios.get("https://coordimeet.eu/googleLogin.php")
            .then(res => {
                if ("googleLoginURL" in res.data)
                    this.loginLink = res.data.googleLoginURL;
                console.log(res.data);
                
            })
        },
    },
    mounted() {
        this.getLoginData();
    }
}
</script>

<style lang="scss" scoped>
@import "../styles/colors";

.header-component {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1rem;
    background-color: $color-top-bottom;

    img {
        height: 200%;
        cursor: pointer;
    }
}
</style>
