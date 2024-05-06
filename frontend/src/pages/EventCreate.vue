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
                    <b class="flex gap-1 items-center">
                        Event type
                        <help-icon class="text-base font-normal">
                            The event type determines who can see and respond to the event:
                            <ul>
                                <li class="ml-5 list-disc">Public - anyone with the invite link can join</li>
                                <!-- <li class="ml-5 list-disc">Closed - only invited people can join</li> -->
                                <li class="ml-5 list-disc">Group - only group members can join</li>
                            </ul>
                        </help-icon>
                    </b>
                    <div class="flex flex-col gap-2 mt-3">
                        <custom-radio
                            type="radio"
                            v-model="eventType"
                            :value="EventType.Public"
                            text="Public"
                        />
                        <custom-radio
                            type="radio"
                            v-model="eventType"
                            :value="EventType.Group"
                            text="Group"
                        />
                    </div>
                </div>
                <div
                    v-if="eventType === EventType.Group"
                    class="flex flex-col gap-2 mb-4"
                >
                    <b class="ml-4">Group</b>
                    <custom-select
                        v-model="groupInvited"
                        :options="groupOptions"
                        placeholder="Please select a group"
                        :disabled="eventType !== EventType.Group"
                    />
                    <b class="mt-4 ml-4 flex gap-1 items-center">
                        Ownership
                        <help-icon class="text-base font-normal">
                            The ownership determines who can edit and finish the event:
                            <ul>
                                <li class="ml-5 list-disc">Event creator - only you can change and edit the event</li>
                                <li class="ml-5 list-disc">Group - all event administrators can edit the event</li>
                            </ul>
                        </help-icon>
                    </b>
                    <custom-toggle
                        class="ml-4"
                        v-model="eventByGroup"
                        :disabled="eventType !== EventType.Group"
                    >
                        <template v-slot:left>
                            <span class="mr-2">Event creator</span>
                        </template>
                        <template v-slot:right>
                            <span class="ml-2">Group</span>
                        </template>
                    </custom-toggle>
                </div>
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
                    <b class="ml-4 flex gap-1 items-center">
                        Rough event duration
                        <help-icon class="text-base font-normal">
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
                        :ignoreValidity="true"
                    />
                </label>
                <label class="flex flex-col gap-2">
                    <b class="ml-4">Response deadline</b>
                    <custom-input
                        type="datetime-local"
                        v-model="deadline"
                    />
                </label>
                <label class="flex flex-col gap-2">
                    <b class="ml-4">Send notifications</b>
                    <div class="ml-3 flex flex-col gap-4">
                        <custom-toggle
                            class="mt-2"
                            v-model="eventNotifications.afterCreation"
                            :right-value="EventNotificationType.Creation"
                        >
                            <template v-slot:right>
                                <span class="ml-2">after event creation</span>
                            </template>
                        </custom-toggle>
                        <custom-toggle
                            v-model="eventNotifications.afterUpdate"
                            :right-value="EventNotificationType.Update"
                        >
                            <template v-slot:right>
                                <span class="ml-2">when the event is updated</span>
                            </template>
                        </custom-toggle>
                        <custom-toggle
                            v-model="eventNotifications.beforeDeadline"
                            :right-value="EventNotificationType.Deadline"
                        >
                            <template v-slot:right>
                                <span class="ml-2">before the deadline</span>
                                <!-- NOTE: Only if not submitted -->
                            </template>
                        </custom-toggle>
                        <custom-toggle
                            v-model="eventNotifications.beforeDateSelected"
                            :right-value="EventNotificationType.EventDateSelected"
                        >
                            <template v-slot:right>
                                <span class="ml-2">when the event date is selected</span>
                                <!-- TODO: send .ics file -->
                            </template>
                        </custom-toggle>
                        <custom-toggle
                            v-model="eventNotifications.beforeEventStart"
                            :right-value="EventNotificationType.EventStart"
                        >
                            <template v-slot:right>
                                <span class="ml-2">before the event starts</span>
                            </template>
                        </custom-toggle>
                    </div>
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
import { initializeDateInput } from "@/utils/dates";

import CustomInput from "@/components/ui/CustomInput.vue";
import CustomButton from "@/components/ui/CustomButton.vue";
import CustomRadio from "@/components/ui/CustomRadio.vue";
import CustomIcon from "@/components/ui/CustomIcon.vue";
import CustomSelect from "@/components/ui/CustomSelect.vue";
import CustomToggle from "@/components/ui/CustomToggle.vue";
import HelpIcon from "@/components/ui/HelpIcon.vue";

import Calendar from "@/components/Calendar.vue";
import TabController from "@/components/TabController.vue";

import { useStoreUser } from "@/stores/storeUser";

import { Event, EventType, EventNotification, EventNotificationType } from "@/types/event";
import { CalendarType, DateRange } from "@/types/calendar";
import { Group } from "@/types/user";
import { SelectOption } from "@/types/ui";
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
            EventType,
            EventNotificationType,
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
        CustomSelect,
        CustomToggle,
        HelpIcon,
    },
    data() {
        return {
            title: "",
            description: "",
            length: 1,
            deadline: initializeDateInput(CalendarType.DateHour),
            eventType: EventType.Public,
            
            calendarType: CalendarType.Date,
            selectedDateRanges: [] as DateRange[],
            fromDate: initializeDateInput(CalendarType.Date),
            toDate: initializeDateInput(CalendarType.Date, undefined, 14),
            eventByGroup: false,

            eventNotifications: {
                afterCreation: false as false|EventNotificationType,
                afterUpdate: false as false|EventNotificationType,
                beforeDeadline: false as false|EventNotificationType,
                beforeEventStart: false as false|EventNotificationType,
                beforeDateSelected: false as false|EventNotificationType,
            },

            groupOptions: [] as SelectOption[],
            groupInvited: undefined as number|undefined,
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

            const eventNotifications = Object.keys(this.eventNotifications)
                .filter((key) => this.eventNotifications[key as keyof typeof this.eventNotifications])
                .map((key) => ({notification_type: this.eventNotifications[key as keyof typeof this.eventNotifications]})
            ) as EventNotification[];

            const event = {
                title: this.title,
                event_calendar_type: this.calendarType,
                event_type: this.eventType,

                organiser: this.user?.id,
                organiser_group: this.eventByGroup ? this.groupInvited : null,
                invited_group: this.groupInvited,

                description: this.description,
                event_length: this.length,
                deadline: new Date(this.deadline),

                event_availability_options: this.selectedDateRanges,
                event_notifications: eventNotifications,
            } as Event;

            ApiService.post("/events/event/", event)
            .then(res => {
                const eventUUID = res.data.event_uuid;
                alert(`Event successfuly created. You will now be redirected to your event page.`)
                this.$router.push(`/event/${eventUUID}`);
            })
            .catch(err => {
                alert("An error occurred while creating the event. Please try again later.");
                console.error(err);
            });
        },
        getGroups() {
            ApiService.get("/users/group/").then((response) => {
                this.groupOptions = response.data.map((group: Group) => {
                    return {
                        value: group.id,
                        text: group.name,
                    } as SelectOption;
                });
            }).catch(() => {
                alert("Failed to fetch user's groups.");
            });
        },
    },
    mounted() {
        this.getGroups();
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
