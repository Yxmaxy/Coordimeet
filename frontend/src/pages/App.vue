<!-- Wrapper page for all other pages -->
<template>
    <div class="app">
        <header-component class="header-section"/>
        <router-view class="page-section"/>
        <footer-component class="footer-section" />
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

<style lang="scss" scoped>
.app {
    height: 100vh;
    display: grid;
    grid-template-areas:
        "header"
        "page"
        "footer";
    grid-template-rows: 3.5rem calc(100vh - 6.5rem) 3rem;
}
.header-section {
    grid-area: header;
}
.page-section {
    grid-area: page;
}
.footer-section {
    grid-area: footer;
}
</style>
