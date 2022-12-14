<!-- Footer on bottom of the page -->
<template>
    <footer class="footer-component">
        &copy;
        <a href="https://vrecer.si">
            Marko
        </a>
        <a href="https://leepush.eu">
            Bine
        </a>
        <a href="https://nikigre.si">
            Nik
        </a>
        <a nolink="true">
            Nika
        </a>
        <a nolink="true">
            Rok
        </a>
    </footer>
</template>

<style lang="scss" scoped>
@import "../styles/colors";
.footer-component {
    display: flex;
    align-items: center;
    padding: 1rem;
    background-color: $color-top-bottom;
    gap: 0.3rem;
    user-select: none;
}
a[nolink=true] {
    cursor: unset;
}
</style>
