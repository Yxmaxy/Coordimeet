<!-- Header on top of the page -->
<template>
    <header class="header-component">
        <img src="/images/logo.png" alt="logo" @click="developmentMode ? $router.push('/event/list') : $router.push('/')"/>
        <user-component />
    </header>
</template>

<script lang="ts">
import { developmentMode } from '../common/globals';
import UserComponent from './UserComponent.vue';

export default {
    components: {
        UserComponent,
    },
    data() {
        return {
            developmentMode,
        }
    }
}
</script>

<style lang="scss" scoped>
@import "../styles/colors";

.header-component {
    user-select: none;
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: {
        left: 1rem;
        right: 1rem;
        top: 0.5rem;
        bottom: 0.5rem;
    };
    background-color: $color-top-bottom;

    & > img {
        height: 100%;
        cursor: pointer;
    }
}
</style>
