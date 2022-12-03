<template>
    <div class="event-page">
        <aside class="responses-area">
            <div>
                Responses
            </div>
        </aside>
        <div class="details-area">
            Event name
        </div>
        <main class="calendar-area">
            <label>
                Select unavailable dates
                <input v-model="selectUnavailable" type="checkbox" />
            </label>
            <calendar
                class="calendar"
                :dateRange="dateRange"
                :selectUnavailable="selectUnavailable"
            />
        </main>
    </div>
</template>

<script lang="ts">
import Calendar from '../components/Calendar.vue';
import { IDateRange } from '../common/interfaces';

export default {
    components: {
        "calendar": Calendar,
    },
    data() {
        return {
            dateRange: {
                from: new Date(2022, 11, 11),
                to: new Date(2022, 11, 19)
            } as IDateRange,
            selectUnavailable: false,
        }
    }
}
</script>

<style lang="scss" scoped>
.event-page {
    flex: 1;
    display: grid;
    grid-template-rows: min(15rem, 30vh) 1fr;
    grid-template-columns: min(20rem, 30vw) 1fr;
    grid-template-areas:
        "responses details"
        "responses calendar";

    .responses-area {
        grid-area: responses;
        background-color: lightcoral;
    }
    .calendar-area {
        grid-area: calendar;
        background-color: lightcyan;
        flex: 1;

        .calendar {
            height: 100%;
            padding: 2rem;
        }
    }
    .details-area {
        grid-area: details;
        background-color: lightsalmon;
    }
}
</style>
