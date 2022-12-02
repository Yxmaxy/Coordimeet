<!-- Wrapper page for all other pages -->
<template>
    <div class="wrapper-page">
       <header-component />
        <div class="page-container">
            <router-view />
        </div>
    </div>
</template>

<script lang="ts">
import Header from "../components/Header.vue";

export default {
    components: {
        "header-component": Header,
    }
}
</script>

<style scoped lang="scss">
header {
    display: flex;
    justify-content: space-between;
    background-color: lightgray;
}
.wrapper-page {
    display: flex;
    flex-direction: column;
    min-height: 100vh;
}
.page-container {
    display: flex;
    flex: 1;
}
</style>
