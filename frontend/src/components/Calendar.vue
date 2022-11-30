<template>
    <div class="calendar">
        <div v-for="label in calendarLabels" class="head">
            {{label}}
        </div>
        <div v-for="day in days">
            {{day}}
        </div>
    </div>
</template>

<script lang="ts">
export default {
    name: "calendar",
    data() {
        return {
            calendarLabels: ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
            days: [] as number[],
        }
    },
    mounted() {
        for (let i = 0; i < 35; i++) {
            this.days.push(i);
        }
    }
}
</script>
<style lang="scss" scoped>
.calendar {
    // variables
    $border-width: 1px;
    $border-color: black;
    box-sizing: border-box;

    // calendar
    display: grid;
    grid-template-columns: repeat(7, 1fr);
    height: 100%;
    width: 100%;
    border: {
        width: calc($border-width / 2);
        style: solid;
        color: $border-color;
    };

    // td
    & > div {
        border: {
            width: $border-width;
            style: solid;
            color: $border-color;
        };
        box-sizing: border-box;
    }

    // table head
    .head {
        background-color: lightgray;
    }
}
</style>