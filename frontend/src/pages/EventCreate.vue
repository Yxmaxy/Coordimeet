<template>
    <tab-controller v-model:activeTab="activeTab" :firstNarrow="true">
        <template v-slot:create_event>
            <div
                class="flex flex-col gap-4 px-4 pt-4 relative
                bg-main-100 min-h-[calc(100vh-7rem)]"
            >
                <label class="flex flex-col gap-2">
                    <b class="ml-4">Event name</b>
                    <custom-input
                        type="text"
                        placeholder="Enter a name for your event"
                        v-model="name"
                    />
                </label>
                <div class="ml-4 mb-4">
                    <b>Select calendar type</b>
                    <div class="flex flex-col gap-2 mt-3">
                        <custom-radio
                            type="radio"
                            v-model="calendarType"
                            :value="CalendarType.Date"
                            text="Date"
                        />
                        <custom-radio
                            type="radio"
                            v-model="calendarType"
                            :value="CalendarType.DateTime"
                            text="Date and time"
                        />
                    </div>
                </div>
                <label class="flex flex-col gap-2">
                    <b class="ml-4">Event length in {{ calendarTypeDisplay }}</b>
                    <custom-input
                        type="number"
                        v-model="length"
                        placeholder="Enter the length of the event"
                        pattern="[0-9]+"
                        invalidMessage="Event length must be a positive integer"
                    />
                </label>
                <div>
                    <b class="ml-4">Rough event duration</b>
                    <div class="ml-4 mr-4 text-xs text-main-700">
                        The rough event duration is used for generating the calendar,
                        where you can select the detailed {{ calendarTypeDisplay }} of the event.
                    </div>
                    <label>
                        <div class="mt-2 ml-4">
                            From
                        </div>
                        <custom-input
                            :type="selectedDateInputType"
                            :modelValue="fromDateComp"
                            @update:modelValue="event => handleDateInput(event.target, 'from')"
                        />
                    </label>
                    <label>
                        <div class="ml-4">
                            To
                        </div>
                        <custom-input
                            :type="selectedDateInputType"
                            :modelValue="toDateComp"
                            @update:modelValue="event => handleDateInput(event.target, 'to')"
                        />
                    </label>
                </div>
                <label class="flex flex-col gap-2">
                    <b class="ml-4">Additional values</b>
                    <custom-input
                        type="textarea"
                        v-model="customFields"
                        placeholder="Enter custom fields eg.
Formal attire: Yes
Ticket price: 5€"
                    />
                </label>
                <label class="flex flex-col gap-2">
                    <b class="ml-4">Deadline</b>
                    <custom-input
                        type="datetime-local"
                        v-model="deadline"
                    />
                </label>
                <custom-button
                    class="mt-3 mb-6"
                    @click="onCreateEvent"
                >
                    Create new event
                </custom-button>
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

import CustomInput from "@/components/ui/CustomInput.vue";
import CustomButton from "@/components/ui/CustomButton.vue";
import CustomRadio from "@/components/ui/CustomRadio.vue";
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
        CustomInput,
        CustomButton,
        CustomRadio,
    },
    data() {
        return {
            calendarType: CalendarType.Date,
            length: 1,
            selectedDates: []  as CalendarDate[],
            fromDate: initializeDateInput(CalendarType.Date),
            toDate: initializeDateInput(CalendarType.Date),
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
