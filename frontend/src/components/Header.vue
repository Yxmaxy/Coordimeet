<!-- Header on top of the page -->
<template>
    <header class="header-component">
        <img src="/images/logo.png" alt="logo" @click="$router.push('/')"/>
        <div>
            <button>Log in</button>
        </div>
    </header>
</template>

<style lang="scss" scoped>
.header-component {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1rem;
    background-color: lightgray;

    img {
        height: 200%;
        cursor: pointer;
    }
}
</style>
