<!-- Header on top of the page -->
<template>
    <header class="header-component">
        <img src="/images/logo.png" alt="logo" @click="$router.push('/')"/>
        <login-button />
    </header>
</template>

<script lang="ts">
import LoginButton from './LoginButton.vue';

export default {
    components: {
        LoginButton,
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

    & > img {
        height: 200%;
        cursor: pointer;
    }
}
</style>
