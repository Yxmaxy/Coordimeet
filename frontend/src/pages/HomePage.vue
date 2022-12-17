<template>
    <div class="home-page">
        <div class="text-area">
            <img class="logo" src="/images/logo.png" alt="CoordiMeet" />
            <div class="description">
                <h2>The solution to all your coordinating needs!</h2>
                <p>Some description</p>
            </div>
        </div>
        <div class="calendar-area">
            <h1></h1>
            <calendar
                :type="type"
                :days="days"
                :dateRanges="dateRanges"
                :disabledMode="true"
            />
        </div>
    </div>
</template>

<script lang="ts">
import { CalendarType, ICalendarDate, IDateRange } from '../common/interfaces';
import Calendar from '../components/Calendar.vue';

export default {
    components: {
        Calendar,
    },
    data() {
        return {
            type: CalendarType.Date,
            days: [] as ICalendarDate[],
            dateRanges: [{
                from: new Date("2022-12-6"),
                to: new Date("2022-12-7")
            }, {
                from: new Date("2022-12-9"),
                to: new Date("2022-12-9")
            }, {
                from: new Date("2022-12-13"),
                to: new Date("2022-12-17")
            }, {
                from: new Date("2022-12-31"),
                to: new Date("2023-1-3")
            }] as IDateRange[],
        }
    },
}
</script>
<style lang="scss" scoped>
@import "../styles/colors.scss";
.home-page {
    background-color: $color-background;
    display: grid;
    grid-template-columns: 2fr 1.5fr;
    grid-template-areas: "text calendar";
    .text-area {
        grid-area: text;
        background-color: $color-background-3;
        padding: 0.75rem;
        h2 {
            text-align: center;
        }
        .description {
            margin-top: 2rem;
        }
    }
    .calendar-area {
        display: flex;
        flex-direction: column;
        grid-area: calendar;
        user-select: none;
        max-height: 500px;
        justify-content: center;
        padding: 0.75rem;
        margin: {
            top: auto;
            bottom: auto;
        }
        height: 100%;
    }
}
</style>
