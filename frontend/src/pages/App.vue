<!-- Wrapper page for all other pages -->
<template>
    <div class="wrapper-page">
       <header-component />
        <div class="page-container">
            <router-view />
        </div>
        <footer-component />
    </div>
</template>

<script lang="ts">
import Header from "../components/Header.vue";
import Footer from "../components/Footer.vue";

export default {
    components: {
        "header-component": Header,
        "footer-component": Footer,
    }
}
</script>

<style scoped lang="scss">
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
