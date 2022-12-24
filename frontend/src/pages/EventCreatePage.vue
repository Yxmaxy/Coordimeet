<template>
    <div class="event-create-page">
        <div class="input-area">
            <h1>Create new event</h1>
            <label>
                <b>Event name</b>
                <input
                    type="text"
                    placeholder="Enter a name for your event"
                    v-model="name"
                    @focusout="() => nameInputRequired = true"
                    :required="nameInputRequired"
                />
            </label>
            <div class="input-subsection">
                <b>Select calendar type</b>
                <div>
                    <label>
                        <input
                            type="radio"
                            v-model="calendarType"
                            :value="CalendarType.Date"
                        />
                        Date
                    </label>
                    <label>
                        <input
                            type="radio"
                            v-model="calendarType"
                            :value="CalendarType.DateTime"
                        />
                        Date and time
                    </label>
                </div>
            </div>
            <label>
                <b>Event length in {{ calendarTypeDisplay }}</b>
                <input
                    type="number"
                    v-model="length"
                    min="1"
                    required
                />
            </label>
            <div class="input-subsection">
                <b>Rough event duration</b>
                <div>
                    <label>
                        From
                        <input
                            :type="selectedDateInputType"
                            :value="fromDateComp"
                            @input="event => handleDateInput(event.target, 'from')"
                            :class="{'invalid': invalidDates}"
                        />
                    </label>
                    <label>
                        To
                        <input
                            :type="selectedDateInputType"
                            :value="toDateComp"
                            @input="event => handleDateInput(event.target, 'to')"
                            :class="{'invalid': invalidDates}"
                        />
                    </label>
                </div>
            </div>
            <label>
                <b>Additional values</b>
                <textarea
                    v-model="customFields"
                    placeholder="Enter custom fields eg.
Formal attire: Yes
Ticket price: 5€"
                ></textarea>
            </label>
            <label>
                <b>Deadline</b>
                <input
                    type="datetime-local"
                    v-model="deadline"
                />
            </label>
            <button id="create-button" @click="onCreateEvent">
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
import axios from 'axios';
import Calendar from '../components/Calendar.vue';
import { useUserStore } from '../common/stores/UserStore';
import { CalendarType, ICalendarDate, IDateRange } from '../common/interfaces';
import { removeHoursMinutesFromDate, initializeDateInput, formatDateForBackend } from '../common/helpers';
import { apiServer } from '../common/globals';

export default {
    setup() {
        const { user } = useUserStore();
        return {
            user,
        }
    },
    components: {
        "calendar": Calendar,
    },
    data() {
        return {
            calendarType: 1,
            length: 1,
            selectedDates: []  as ICalendarDate[],
            fromDate: initializeDateInput(1),
            toDate: initializeDateInput(1),
            invalidDates: false,
            selectedDateRanges: [] as IDateRange[],
            customFields: "",
            deadline: initializeDateInput(CalendarType.DateTime),

            // name input
            name: "",
            nameInputRequired: false,

            CalendarType,
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
        fromDateComp() {
            return initializeDateInput(this.calendarType, this.fromDate);
        },
        toDateComp() {
            return initializeDateInput(this.calendarType, this.toDate);
        },
    },
    methods: {
        getDateRanges() {
            this.invalidDates = false;
            const now = new Date();
            const from = this.fromDate.length > 0 ? removeHoursMinutesFromDate(new Date(this.fromDate)) : new Date(now.getFullYear(), now.getMonth(), now.getDate());
            const to = this.toDate.length > 0 ? removeHoursMinutesFromDate(new Date(this.toDate)) :  new Date(now.getFullYear(), now.getMonth(), now.getDate(), 23);
            
            if (from > to) {
                this.invalidDates = true;
                return;
            }

            this.selectedDateRanges = [{
                from: from,
                to: to,
            }];
        },
        onCreateEvent() {
            if (this.name.length === 0) {
                this.nameInputRequired = true;
                alert("You must enter a name for the event");
                return;
            }
            if (this.length < 0) {
                alert("Event length must me bigger or equal to 1");
                return;
            }
            
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
                        StartDate: formatDateForBackend(new Date(currentStart)),
                        EndDate: formatDateForBackend(new Date(prevDate.date)),
                    })
                    currentStart = undefined;
                }
            }
            if (dates.length === 0) {
                alert(`Please select the ${this.calendarTypeDisplay} on the calendar, on which you would like the event to happen.`)
                return;
            }
            
            axios.post(`${apiServer}/event.php?`, {
                Event: {
                    IDOrganizer: this.user.GoogleID,
                    Name: this.name,
                    Length: this.length,
                    CalendarType: this.calendarType,
                    Deadline: formatDateForBackend(new Date(this.deadline)),
                    Config: config,
                },
                EventRanges: dates,
            })
            .then(res => {
                console.log(res.data);
            })
        },
        handleDateInput(target: EventTarget|null, type: 'from'|'to') {
            const input = target as HTMLInputElement;
            if (type === 'from')
                this.fromDate = input.value;
            else
                this.toDate = input.value;
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
@import "../styles/colors";
.event-create-page {
    $sectionPadding: 1rem;

    flex: 1;
    display: grid;
    grid-template-columns: min(35rem, 35vw) 1fr;
    grid-template-areas:
        "input calendar"
        "input calendar";

    .input-area {
        grid-area: input;
        background-color: $color-background-3;
        overflow: auto;
        padding: $sectionPadding;
        display: flex;
        flex-direction: column;
        gap: 1.5rem;
        position: relative;

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
        background-color: $color-background;
        display: flex;
        flex-direction: column;
        padding: $sectionPadding;
        overflow: auto;
        .controls {
            position: sticky;
            top: 0;
        }
    }
    #create-button {
        position: sticky;
        bottom: $sectionPadding;
        left: $sectionPadding;
        right: $sectionPadding;
    }
}
</style>
