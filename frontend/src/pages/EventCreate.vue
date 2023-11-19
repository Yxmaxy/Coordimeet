<template>
    <tab-controller :tabs="tabs">
        <template v-slot:create_event>
            <div
                class="flex flex-col gap-4 px-4 pt-4 h-full
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
    formatDateForBackend } from "@/utils/dates";

import CustomInput from "@/components/ui/CustomInput.vue";
import CustomButton from "@/components/ui/CustomButton.vue";
import CustomRadio from "@/components/ui/CustomRadio.vue";
import Calendar from "@/components/Calendar.vue";
import TabController from "@/components/TabController.vue";

import { useUserStore } from "@/stores/UserStore";

import { CalendarType, DateRange } from "@/types/calendar";
import { Tab } from "@/types/tabs";

const tabs = [
    {
        name: "Create new event",
        slot_name: "create_event",
        narrow: "md",
    },
    {
        name: "Calendar input",
        slot_name: "calendar_input",
    }
] as Tab[];

export default {
    setup() {
        const { user } = useUserStore();
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
    },
    data() {
        return {
            name: "",
            length: 1,
            customFields: "",
            deadline: initializeDateInput(CalendarType.DateTime),
            
            calendarType: CalendarType.Date,
            selectedDateRanges: [] as DateRange[],
            fromDate: initializeDateInput(CalendarType.Date),
            toDate: initializeDateInput(CalendarType.Date),
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
            return this.fromDate < this.toDate;
        },
        roughEventDateRange(): DateRange {
            return {
                from: new Date(this.fromDate),
                to: new Date(this.toDate),
            }
        },
    },
    methods: {
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
            const dates = this.selectedDateRanges.map(dateRange => {
                return {
                    StartDate: formatDateForBackend(dateRange.from),
                    EndDate: formatDateForBackend(dateRange.to),
                }
            });

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
    },
    watch: {
        calendarType(newType: CalendarType) {
            this.toDate = initializeDateInput(newType, this.toDate);
            this.fromDate = initializeDateInput(newType, this.fromDate);
        },
    },
}
</script>
