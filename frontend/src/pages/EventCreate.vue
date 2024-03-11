<template>
    <tab-controller :tabs="tabs">
        <template v-slot:create_event>
            <div
                class="flex flex-col gap-4 px-4 pt-4 h-full
                bg-main-100 min-h-[calc(100vh-7rem)]"
            >
                <label class="flex flex-col gap-2">
                    <b class="ml-4">Event title</b>
                    <custom-input
                        type="text"
                        placeholder="Enter a title for your event"
                        v-model="title"
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
                            :value="CalendarType.DateHour"
                            text="Date and hour"
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
                    <b class="ml-4 flex gap-2 items-center">
                        Rough event duration
                        <help-icon class="text-base">
                            The rough event duration is used for generating the calendar,
                            where you can select the detailed {{ calendarTypeDisplay }} of the event.
                        </help-icon>
                    </b>
                    <label>
                        <div class="mt-2 ml-4">
                            From
                        </div>
                        <custom-input
                            :type="selectedDateInputType"
                            v-model="fromDate"
                            :forceInvalidMessage="areDatesInvalid"
                            invalidMessage="The 'From' date can't be after the 'To' date"
                        />
                    </label>
                    <label>
                        <div class="ml-4">
                            To
                        </div>
                        <custom-input
                            :type="selectedDateInputType"
                            v-model="toDate"
                            :forceInvalidMessage="areDatesInvalid"
                            invalidMessage="The 'From' date can't be after the 'To' date"
                        />
                    </label>
                </div>
                <label class="flex flex-col gap-2">
                    <b class="ml-4">Description</b>
                    <custom-input
                        type="textarea"
                        v-model="description"
                        placeholder="Enter a description of the event"
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
                    Create new event <custom-icon class="text-base" icon="event_available" />
                </custom-button>
            </div>
        </template>
        <template v-slot:calendar_input>
            <div class="bg-main-000 h-full">
                <calendar
                    v-model:selectedDateRanges="selectedDateRanges"
                    :roughEventDateRange="roughEventDateRange"
                    :calendarType="calendarType"
                />
            </div>
        </template>
    </tab-controller>
</template>

<script lang="ts">
import ApiService from "@/utils/ApiService";
import {
    initializeDateInput,
    formatDateForBackend,
    convertDateRangesForBackend } from "@/utils/dates";

import CustomInput from "@/components/ui/CustomInput.vue";
import CustomButton from "@/components/ui/CustomButton.vue";
import CustomRadio from "@/components/ui/CustomRadio.vue";
import CustomIcon from "@/components/ui/CustomIcon.vue";
import HelpIcon from "@/components/ui/HelpIcon.vue";

import Calendar from "@/components/Calendar.vue";
import TabController from "@/components/TabController.vue";

import { useStoreUser } from "@/stores/storeUser";

import { Event } from "@/types/event";
import { CalendarType, DateRange } from "@/types/calendar";
import { Tab } from "@/types/tabs";

const tabs = [
    {
        name: "Create new event",
        slot_name: "create_event",
        narrow: "md",
        icon: "calendar_add_on",
    },
    {
        name: "Calendar input",
        slot_name: "calendar_input",
        icon: "calendar_month",
    }
] as Tab[];

export default {
    setup() {
        const { user } = useStoreUser();
        return {
            user,
            CalendarType,
            tabs,
        }
    },
    components: {
        Calendar,
        TabController,
        CustomInput,
        CustomButton,
        CustomRadio,
        CustomIcon,
        HelpIcon,
    },
    data() {
        return {
            title: "",
            description: "",
            length: 1,
            deadline: initializeDateInput(CalendarType.DateHour),
            
            calendarType: CalendarType.Date,
            selectedDateRanges: [] as DateRange[],
            fromDate: initializeDateInput(CalendarType.Date),
            toDate: initializeDateInput(CalendarType.Date, undefined, 14),
        }
    },
    computed: {
        calendarTypeDisplay() {
            if (this.calendarType === CalendarType.Date)
                return "days";
            return "hours";
        },
        selectedDateInputType(): string {
            if (this.calendarType === CalendarType.Date)
                return "date";
            return "datetime-local";
        },
        areDatesInvalid(): boolean {
            return this.roughEventDateRange.start_date.getTime() > this.roughEventDateRange.end_date.getTime();
        },
        roughEventDateRange(): DateRange {
            return {
                start_date: new Date(this.fromDate),
                end_date: new Date(this.toDate),
            }
        },
    },
    methods: {
        onCreateEvent() {
            if (this.title.length === 0) {
                alert("You must enter a title for the event");
                return;
            }
            if (this.length < 0) {
                alert("Event length must me bigger or equal to 1");
                return;
            }

            // check if dates were selected
            if (this.selectedDateRanges.length === 0) {
                alert(`Please select the ${this.calendarTypeDisplay} on the calendar, on which you would like the event to happen.`)
                return;
            }

            const event = {
                title: this.title,
                description: this.description,
                event_calendar_type: this.calendarType,
                event_length: this.length,
                deadline: new Date(this.deadline),
                event_availability_options: this.selectedDateRanges,
            } as Event;
            console.log(event);
            ApiService.post(`/events/event/`, event)
            .then(res => {
                const IDEvent = res.data.IDEvent;
                alert(`Event successfuly created. You will now be redirected to your event page.`)
                this.$router.push(`/event/${IDEvent}`);
            })
        },
    },
    watch: {
        calendarType(newType: CalendarType) {
            this.toDate = initializeDateInput(newType, this.toDate);
            this.fromDate = initializeDateInput(newType, this.fromDate);
            this.selectedDateRanges = [];
        },
    },
}
</script>
