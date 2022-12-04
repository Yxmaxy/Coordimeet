<template>
    <div class="event-page">
        <aside class="responses-area">
            <h1>Responses</h1>
            <div>
                <div v-for="index in 50" class="response">
                    <div>Ime</div>
                    <div>Odgovor</div>
                </div>
            </div>
        </aside>
        <div class="details-area">
            <h1>Dogodek 1</h1>
            <div>Deadline: 3. 12. 2022</div>
            <div>Trajanje: 11. 12. 2022 - 19. 12. 2022</div>
        </div>
        <main class="calendar-area">
            <calendar
                :type="calendarType"
                :dateRange="dateRange"
            />
        </main>
    </div>
</template>

<script lang="ts">
import Calendar from '../components/Calendar.vue';
import { IDateRange, CalendarType } from '../common/interfaces';

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
            calendarType: CalendarType.DateTime,
        }
    }
}
</script>

<style lang="scss" scoped>
.event-page {
    $sectionPadding: 0.5rem;

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
        overflow: auto;

        h1 {
            background-color: lightcoral;
            padding: $sectionPadding;
            position: sticky;
            top: 0;
        }

        .response {
            display: flex;
            justify-content: space-between;
            padding: $sectionPadding;
        }
    }
    .calendar-area {
        grid-area: calendar;
        background-color: lightcyan;
        display: flex;
        flex-direction: column;
        padding: $sectionPadding;
        overflow: auto;
        .controls {
            position: sticky;
            top: 0;
        }
    }
    .details-area {
        grid-area: details;
        background-color: lightsalmon;
        padding: $sectionPadding;
    }
}
</style>
