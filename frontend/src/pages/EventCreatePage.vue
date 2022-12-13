<template>
    <div class="event-create-page">
        <div class="input-area">
            <h1>Event data</h1>
            <label>
                Event name
                <input
                    type="text"
                    placeholder="Enter a name for your event"
                    v-model="name"
                />
            </label>
            <div class="checkbox-section">
                Select calendar type
                <div>
                    <label>
                        <input
                            type="radio"
                            v-model="calendarType"
                            :value="1"
                        />
                        Date
                    </label>
                    <label>
                        <input
                            type="radio"
                            v-model="calendarType"
                            :value="0"
                        />
                        Date and time
                    </label>
                </div>
            </div>
            <label>
                Event length in {{ calendarTypeDisplay }}
                <input
                    type="number"
                    v-model="length"
                    min="1"
                />
            </label>
        </div>
        <main class="calendar-area">
            <!-- <calendar
                :type="eventData.CalendarType"
                :dateRanges="eventData.EventDates"
                :days="selectedDates"
            /> -->
        </main>
    </div>
</template>

<script lang="ts">
import Calendar from '../components/Calendar.vue';
import { CalendarType } from '../common/interfaces';

export default {
    components: {
        "calendar": Calendar,
    },
    data() {
        return {
            name: "",
            calendarType: 0,
            length: 1,
        }
    },
    computed: {
        calendarTypeDisplay() {
            console.log(this.calendarType, CalendarType.Date);
            
            if (this.calendarType === CalendarType.Date)
                return "days";
            return "hours";
        }
    },
    methods: {
        onSubmitEvent() {
            
        }
    },
}
</script>

<style lang="scss" scoped>
.event-create-page {
    $sectionPadding: 0.5rem;

    flex: 1;
    display: grid;
    grid-template-columns: min(35rem, 35vw) 1fr;
    grid-template-areas:
        "input calendar"
        "input calendar";

    .input-area {
        grid-area: input;
        background-color: lightcoral;
        overflow: auto;
        padding: $sectionPadding;
        display: flex;
        flex-direction: column;
        gap: 1rem;

        & > label, div[class=checkbox-section] {
            display: flex;
            flex-direction: column;
            gap: 0.5rem;
        }

        div[class=checkbox-section] div {
            display: flex;
            flex-direction: column;
            gap: 0.2rem;
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
        position: relative;

        #submit-response {
            position: absolute;
            right: 0;
            bottom: 0;
        }
    }
}
</style>
