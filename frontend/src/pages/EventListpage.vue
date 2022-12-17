<template>
    <div class="event-list-page">
        <div>
            <h1>Events I'm invited to</h1>
            <div>
                <div class="event" v-for="x in 100">
                    <div><b>Name</b></div>
                    <div>
                        <div>Deadline</div>
                        <div>Organiser</div>
                    </div>
                </div>
            </div>
        </div>
        <div>
            <h1>
                <div>Events I've created</div>
                <button @click="$router.push('/event/new')">New event</button>
            </h1>
        </div>
    </div>
</template>

<script lang="ts">
export default {
    data() {
        return {
            events: []  // events from api
        }
    }
}
</script>

<style lang="scss" scoped>
@import "../styles/colors.scss";
.event-list-page {
    $sectionPadding: 1rem;

    display: grid;
    grid-template-columns: 1fr 1fr;

    & > div {
        overflow: auto;
        &:first-child {
            border-right: 2px solid $color-top-bottom;
        }
        h1 {
            position: sticky;
            top: 0;
            display: flex;
            justify-content: space-between;
            align-items: center;
            z-index: 10;
            
            background-color: $color-background-3;
            padding: $sectionPadding;
        }

        .event {
            background-color: $color-background-3;
            margin: 0.75rem;
            padding: 1.25rem;
            border-radius: 20px;
            display: flex;
            justify-content: space-between;
            cursor: pointer;
            transition: 200ms;

            &:hover {
                background-color: $color-top-bottom;
                transform: translateY(-0.1rem);
            }

            & > div {
                display: flex;
                gap: 0.75rem;
            }
        }
    }
}
</style>
