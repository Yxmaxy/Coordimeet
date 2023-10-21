<template>
    <tab-controller v-model:activeTab="activeTab" :firstNarrow="true">
        <template v-slot:create_event>
            <div
                class="flex flex-col gap-4 px-4 pt-4 relative
                bg-main-100 min-h-[calc(100vh-7rem)]"
            >
                <label class="flex flex-col gap-2">
                    <span class="font-bold ml-4">Event name</span>
                    <input-element
                        type="text"
                        placeholder="Enter a name for your event"
                        v-model="name"
                    />
                </label>
                <div class="ml-1.5">
                    <span class="font-bold">Select calendar type</span>
                    <div class="flex flex-col gap-3 mt-3">
                        <input-element
                            type="radio"
                            v-model="calendarType"
                            :value="CalendarType.Date"
                            placeholder="Date"
                        />
                        <input-element
                            type="radio"
                            v-model="calendarType"
                            :value="CalendarType.DateTime"
                            placeholder="Date and time"
                        />
                    </div>
                </div>

                <!-- TODO: checked to here -->

                <label class="flex flex-col gap-2">
                    <b>Event length in {{ calendarTypeDisplay }}</b>
                    <input-element
                        type="number"
                        v-model="length"
                        :min="1"
                        placeholder="Enter the length of the event"
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
                <label class="flex flex-col gap-2">
                    <b>Additional values</b>
                    <textarea
                        v-model="customFields"
                        placeholder="Enter custom fields eg.
Formal attire: Yes
Ticket price: 5€"
                    ></textarea>
                </label>
                <label class="flex flex-col gap-2">
                    <b>Deadline</b>
                    <input
                        type="datetime-local"
                        v-model="deadline"
                    />
                </label>
                <button
                    class="btn absolute bottom-3 left-3 right-3"
                    @click="onCreateEvent"
                >
                    Create new event
                </button>
            </div>
        </template>
        <template v-slot:calendar_input>
            <calendar
                :type="calendarType"
                :days="selectedDates"
                :dateRanges="selectedDateRanges"
                :insertMode="true"
            />
        </template>
    </tab-controller>
</template>

<script lang="ts">
import ApiService from "@/utils/ApiService";
import {
    removeHoursMinutesFromDate,
    initializeDateInput,
    formatDateForBackend,
    getSelectedDatesOnCalendar } from "@/utils/dates";

import InputElement from "@/components/ui/InputElement.vue";
import Calendar from "@/components/Calendar.vue";
import TabController from "@/components/TabController.vue";

import { useUserStore } from "@/stores/UserStore";

import { CalendarType, CalendarDate, DateRange } from "@/types/calendar";

export default {
    setup() {
        const { user } = useUserStore();
        return {
            user,
        }
    },
    components: {
        Calendar,
        TabController,
        InputElement,
    },
    data() {
        return {
            calendarType: 1,
            length: 1,
            selectedDates: []  as CalendarDate[],
            fromDate: initializeDateInput(1),
            toDate: initializeDateInput(1),
            invalidDates: false,
            selectedDateRanges: [] as DateRange[],
            customFields: "",
            deadline: initializeDateInput(CalendarType.DateTime),

            name: "",

            CalendarType,

            activeTab: 0 as number,
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
            const dates = getSelectedDatesOnCalendar(this.selectedDates);

            if (dates.length === 0) {
                alert(`Please select the ${this.calendarTypeDisplay} on the calendar, on which you would like the event to happen.`)
                return;
            }

            ApiService.post("event.php", {
                Event: {
                    IDOrganizer: this.user!.GoogleID,
                    Name: this.name,
                    Length: this.length,
                    CalendarType: this.calendarType,
                    Deadline: formatDateForBackend(new Date(this.deadline)),
                    Config: config,
                    SelectedDate: null,
                },
                EventRanges: dates,
            })
            .then(res => {
                const IDEvent = res.data.IDEvent;
                alert(`Event successfuly created. You will now be redirected to your event page.`)
                this.$router.push(`/event/${IDEvent}`);
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
