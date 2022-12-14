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
            <div class="input-subsection">
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
            <div class="input-subsection">
                Rough event duration
                <div>
                    <label>
                        From
                        <input
                            :type="selectedDateInputType"
                            v-model="fromDate"
                        />
                    </label>
                    <label>
                        To
                        <input
                            :type="selectedDateInputType"
                            v-model="toDate"
                        />
                    </label>
                </div>
            </div>
            <label>
                Additional values
                <textarea
                    v-model="customFields"
                    placeholder="Enter custom fields eg.
Formal attire: Yes
Ticket price: 5€"
                ></textarea>
            </label>
            <button @click="onCreateEvent">
                Create new event
            </button>
        </div>
        <main class="calendar-area">
            <calendar
                :type="calendarType"
                :days="selectedDates"
                :dateRanges="selectedDateRanges"
                :insertMode="true"
            />
        </main>
    </div>
</template>

<script lang="ts">
import Calendar from '../components/Calendar.vue';
import { CalendarType, ICalendarDate, IDateRange } from '../common/interfaces';
import { removeHoursMinutesFromDate } from '../common/helpers';
export default {
    components: {
        "calendar": Calendar,
    },
    data() {
        return {
            name: "",
            calendarType: 1,
            length: 1,
            selectedDates: []  as ICalendarDate[],
            fromDate: "",
            toDate: "",
            selectedDateRanges: [] as IDateRange[],
            customFields: "",
        }
    },
    computed: {
        calendarTypeDisplay() {
            if (this.calendarType === CalendarType.Date)
                return "days";
            return "hours";
        },
        selectedDateInputType() {
            if (this.calendarType === CalendarType.Date)
                return "date";
            return "datetime-local";
        },
    },
    methods: {
        getDateRanges() {
            const now = new Date();
            const from = this.fromDate.length > 0 ? removeHoursMinutesFromDate(new Date(this.fromDate)) : new Date(now.getFullYear(), now.getMonth(), now.getDate());
            const to = this.toDate.length > 0 ? removeHoursMinutesFromDate(new Date(this.toDate)) :  new Date(now.getFullYear(), now.getMonth(), now.getDate(), 23);
            
            this.selectedDateRanges = [{
                from: from,
                to: to,
            }];
        },
        onCreateEvent() {
            // calculate config
            const config: any = {}
            if (this.customFields.length > 0) {
                for (const line of this.customFields.split("\n")) {
                    const splitted = line.split(":");
                    if (splitted.length === 2) {
                        config[splitted[0].trim()] = splitted[1].trim();
                    }
                }
            }

            // calculate dates
            const dates: any = [];
            let currentStart: Date|undefined = undefined;
            for (let i = 0; i < this.selectedDates.length; i++) {
                const date = this.selectedDates[i];
                if (currentStart === undefined && date.isAvailable)  // set currentStart
                    currentStart = date.date;
                else if (currentStart !== undefined && !date.isAvailable) {  // add prevDate to dates
                    const prevDate = this.selectedDates[i - 1];
                    dates.push({
                        StartDate: new Date(currentStart),
                        EndDate: new Date(prevDate.date),
                    })
                    currentStart = undefined;
                }
            }

            console.log({
                Event: {
                    IDOrganizer: 1,
                    Name: this.name,
                    Length: this.length,
                    UrlJoinLink: "https://coordimeet.eu/joinEvent?id=123",
                    CalendarType: this.calendarType,
                    Config: config
                },
                EventRanges: dates,
            });
        }
    },
    watch: {
        fromDate() {
            this.getDateRanges();
        },
        toDate() {
            this.getDateRanges();
        },
        calendarType() {
            this.getDateRanges();
        },
    },
    mounted() {
        this.getDateRanges();
    }
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
        gap: 1.5rem;

        input[type=text], input[type=date], input[type=datetime-local], textarea {
            box-sizing: border-box;
            width: 100%;
        }

        textarea {
            min-height: 10ch;
        }

        & > label, div[class=input-subsection] {
            display: flex;
            flex-direction: column;
            gap: 0.4rem;
        }

        div[class=input-subsection] div {
            display: flex;
            flex-direction: column;
            gap: 0.3rem;
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
