<template>
    <div class="home-page">
        <img class="logo" src="/images/logo.png" alt="CoordiMeet" />
    </div>
</template>

<style lang="scss" scoped>
@import "../styles/colors.scss";
.home-page {
    background-color: $color-background;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    overflow: auto;
    img {
        width: min(50rem, 100%);
    }
}
</style>
