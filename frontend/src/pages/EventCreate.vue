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
                        <div class="flex flex-row items-center gap-2">
                            <custom-radio
                                type="radio"
                                v-model="eventType"
                                :value="EventType.Group"
                                text="Group"
                                :disabled="groupOptions.length === 0"
                            />
                            <help-icon
                                v-if="groupOptions.length === 0"
                                class="text-base font-normal"
                            >
                                You need to be a member of a group to create a group event.
                            </help-icon>
                        </div>
                        <div class="flex flex-row items-center gap-2">
                            <custom-radio
                                type="radio"
                                v-model="eventType"
                                :value="EventType.Closed"
                                text="Closed"
                            />
                            <help-icon
                                class="text-base font-normal"
                            >
                                You can invite users by their email address. A temporary group will be created.
                            </help-icon>
                        </div>
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
                        v-model="isGroupOrganiser"
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
                <div
                    v-if="eventType === EventType.Closed"
                    class="flex flex-col gap-2 mb-4"
                >
                    <b class="ml-4">Invited users</b>
                    <div>
                        <div class="flex gap-2">
                            <custom-input
                                type="email"
                                v-model="closedGroupUserEmail"
                                placeholder="Enter a user's email address"
                                :forceInvalidMessage="closedGroupUserForceInvalidMessage"
                                :invalidMessage="closedGroupMemberInvalidMessage"
                                @keydown.enter="addClosedGroupMember"
                                @input="closedGroupUserForceInvalidMessage = false"
                            />
                            <custom-button
                                class="h-11 rounded-xl"
                                :click="addClosedGroupMember"
                            >
                                <custom-icon icon="add" />
                            </custom-button>
                        </div>
                        <div class="flex flex-col gap-4 mt-1">
                            <div
                                v-for="closedGroupUser in closedGroupUsers"
                                class="flex justify-between items-center bg-main-000 px-6 py-4 rounded-2xl shadow-md"
                            >
                                <div class="flex gap-1 items-center">
                                    <b class="flex items-center h-8">{{ closedGroupUser.email }}</b>
                                    <help-icon
                                        v-if="!closedGroupUser.exists"
                                        class="text-base font-normal text-calendar-unavailable" icon="info"
                                    >
                                        This user doesn't exist yet.
                                        <br /><br />
                                        You can send them the following link to create an account:
                                        <div
                                            class="cursor-pointer font-mono"
                                            @click="copyInviteLink"
                                        >
                                            {{ inviteLink }}
                                        </div>
                                    </help-icon>
                                </div>    
                                <div class="flex gap-2">
                                    <custom-button
                                        class="h-8 w-8 rounded-full"
                                        :click="() => deleteMember(closedGroupUser)"
                                    >
                                        <custom-icon icon="delete" />
                                    </custom-button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="ml-4 mb-4">
                    <b>Select calendar type</b>
                    <div v-if="calendarType" class="flex flex-col gap-2 mt-3">
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
                <div v-if="eventType !== EventType.Public" class="flex flex-col gap-2">
                    <b class="ml-4">Send notifications</b>
                    <div class="ml-3 flex flex-col gap-4">
                        <custom-toggle
                            class="mt-2"
                            v-model="eventNotifications.afterCreation"
                        >
                            <template v-slot:right>
                                <span class="ml-2">after the event is created</span>
                            </template>
                        </custom-toggle>

                        <custom-toggle
                            v-model="eventNotifications.afterUpdate"
                        >
                            <template v-slot:right>
                                <span class="ml-2">when the event is updated</span>
                            </template>
                        </custom-toggle>

                        <div class="flex flex-col gap-1">
                            <custom-toggle
                                v-model="eventNotifications.beforeDeadline"
                            >
                                <template v-slot:right>
                                    <div class="ml-2 flex gap-1 items-center">
                                        <div>before the deadline</div>
                                        <help-icon @click.stop>
                                            Notify the participants who haven't responded yet, that the deadline is approaching.
                                        </help-icon>
                                    </div>
                                </template>
                            </custom-toggle>
                            <label
                                v-if="eventNotifications.beforeDeadline"
                                class="ml-8"
                            >
                                <custom-input
                                    type="datetime-local"
                                    v-model="eventNotificationsDeadline"
                                    :required="eventNotifications.beforeDeadline"
                                />
                            </label>
                        </div>

                        <!-- Implement in the selection
                        <custom-toggle
                            v-model="eventNotifications.beforeDateSelected"
                            :right-value="EventNotificationType.EventDateSelected"
                        >
                            <template v-slot:right>
                                <span class="ml-2">when the event date is selected</span>
                                TODO: send .ics file
                            </template>
                        </custom-toggle>

                        <custom-toggle
                            v-model="eventNotifications.beforeEventStart"
                            :right-value="EventNotificationType.EventStart"
                        >
                            <template v-slot:right>
                                <span class="ml-2">before the event starts</span>
                            </template>
                        </custom-toggle> -->
                    </div>
                </div>
                <custom-button
                    v-if="!isEditing"
                    class="mt-3 mb-6"
                    @click="onCreateEvent"
                >
                    Create new event <custom-icon class="text-base" icon="event_available" />
                </custom-button>
                <custom-button
                    v-else
                    class="mt-3 mb-6"
                    @click="onUpdateEvent"
                >
                    Update event <custom-icon class="text-base" icon="edit_calendar" />
                </custom-button>
            </div>
        </template>
        <template v-slot:calendar_input>
            <div class="bg-main-000 h-full">
                <calendar
                    v-if="calendarType"
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
import { initializeDateInput, addUnitsToDate } from "@/utils/dates";

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
import { useStoreMessages } from "@/stores/storeMessages";

import { Event, EventType, EventNotification, EventNotificationType } from "@/types/event";
import { CalendarType, DateRange } from "@/types/calendar";
import { Group, User } from "@/types/user";
import { SelectOption } from "@/types/ui";
import { Tab } from "@/types/tabs";

interface UserCreate extends User {
    exists: boolean;
}
interface EventCreate extends Event {
    closed_group_users: User[],
}

export default {
    setup() {
        const { user } = useStoreUser();
        const storeMessages = useStoreMessages();
        return {
            CalendarType,
            EventType,
            EventNotificationType,

            user,
            storeMessages,

            inviteLink: `${import.meta.env.VITE_FRONTEND_URL}/`,
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
            deadline: initializeDateInput(CalendarType.DateHour, undefined, 1),
            eventType: EventType.Public,
            
            calendarType: null as CalendarType|null,
            selectedDateRanges: [] as DateRange[],
            fromDate: initializeDateInput(CalendarType.Date),
            toDate: initializeDateInput(CalendarType.Date, undefined, 14),
            isGroupOrganiser: false,

            eventNotifications: {
                afterCreation: false,
                afterUpdate: false,
                beforeDeadline: false,
            },
            eventNotificationsDeadline: initializeDateInput(CalendarType.DateHour, undefined, 1),

            groupOptions: [] as SelectOption[],
            groupInvited: undefined as number|undefined,

            closedGroupUsers: [] as UserCreate[],
            closedGroupUserEmail: "",
            closedGroupUserForceInvalidMessage: false,
            closedGroupMemberInvalidMessage: "",
        }
    },
    computed: {
        tabs() {
            return [
                {
                    name: this.isEditing ? "Editing event" : "Create new event",
                    slot_name: "create_event",
                    narrow: "md",
                    icon: this.isEditing ? "edit_calendar" : "calendar_add_on",
                },
                {
                    name: "Calendar input",
                    slot_name: "calendar_input",
                    icon: "calendar_month",
                }
            ] as Tab[];
        },
        isEditing() {
            return this.$route.name === "event_edit";
        },
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
        getValidatedEventData() {
            if (this.title.length === 0) {
                this.storeMessages.showMessageError("You must enter a title for the event");
                return;
            }
            if (!this.length || this.length < 0) {
                this.storeMessages.showMessageError("Event length must me bigger or equal to 1");
                return;
            }

            // check that all selected date ranges have length equal of bigger to this.length
            for (const dateRange of this.selectedDateRanges) {
                let units = 1;  // if a date range is selected, it must have at least 1 unit
                let startDate = dateRange.start_date;
                while (startDate.getTime() < dateRange.end_date.getTime()) {
                    startDate = this.addUnitsToDate(new Date(startDate), this.calendarType!, 1);
                    units++;
                }
                if (units < this.length) {
                    this.storeMessages.showMessageError(`All selected calendar ranges should be equal or longer than ${this.length} ${this.calendarTypeDisplay} (set in Event length)`);
                    return;
                }
            }

            // check if dates were selected
            if (this.selectedDateRanges.length === 0) {
                this.storeMessages.showMessageError(`Please select the ${this.calendarTypeDisplay} on the calendar, on which you would like the event to happen.`)
                return;
            }

            // check that the deadline is before the first selected date
            if (new Date(this.deadline) > this.selectedDateRanges[0].start_date) {
                this.storeMessages.showMessageError("The deadline must be before the event starts.");
                return;
            }

            // check that the deadline notification is before the deadline
            if (this.eventNotifications.beforeDeadline && new Date(this.eventNotificationsDeadline) > new Date(this.deadline)) {
                this.storeMessages.showMessageError("The deadline notification must be sent before the deadline.");
                return;
            }

            // if the event type is group, groupInvited must be selected
            if (this.eventType === EventType.Group && !this.groupInvited) {
                this.storeMessages.showMessageError("Please select a group to invite.");
                return;
            }

            // if the event type is closed, closedMembers must have something inside
            if (this.eventType === EventType.Closed && this.closedGroupUsers.length === 0) {
                this.storeMessages.showMessageError("Please add at least one member to this event in the Invited users section.");
                return;
            }

            const eventNotifications = [] as EventNotification[];
            if (this.eventNotifications.afterCreation)
                eventNotifications.push({ notification_type: EventNotificationType.Creation });
            if (this.eventNotifications.afterUpdate)
                eventNotifications.push({ notification_type: EventNotificationType.Update });
            if (this.eventNotifications.beforeDeadline)
                eventNotifications.push({
                    notification_type: EventNotificationType.Deadline,
                    notification_time: new Date(this.eventNotificationsDeadline)
                });

            return {
                title: this.title,
                event_calendar_type: this.calendarType,
                event_type: this.eventType,

                organiser: this.user?.id,
                is_group_organiser: this.isGroupOrganiser,
                invited_group: this.groupInvited,

                closed_group_users: this.closedGroupUsers.map(user => ({email: user.email})),

                description: this.description,
                event_length: this.length,
                deadline: new Date(this.deadline),

                event_availability_options: this.selectedDateRanges,
                event_notifications: eventNotifications,
            } as EventCreate;
        },
        onCreateEvent() {
            const event = this.getValidatedEventData();
            if (!event)
                return;

            ApiService.post("/events/event/", event)
            .then(res => {
                const eventUUID = res.data.event_uuid;
                this.storeMessages.showMessage(`Event successfuly created. You will now be redirected to your event page.`)
                this.$router.push(`/event/${eventUUID}`);
            })
            .catch(err => {
                this.storeMessages.showMessageError("An error occurred while creating the event. Please try again later.");
                console.error(err);
            });
        },
        onUpdateEvent() {
            const event = this.getValidatedEventData();
            if (!event)
                return;

            // if event is type Closed, remove invited_group
            if (event.event_type === EventType.Closed)
                event.invited_group = undefined;

            ApiService.put(`/events/event/${this.$route.params.uuid}/`, event)
            .then(() => {
                this.storeMessages.showMessage(`Event successfuly updated. You will now be redirected to your event page.`)
                this.$router.push(`/event/${this.$route.params.uuid}`);
            })
            .catch(err => {
                this.storeMessages.showMessageError("An error occurred while creating the event. Please try again later.");
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
                if (this.groupOptions.length === 1 && !this.groupInvited) {
                    if (!this.isEditing)
                        this.groupInvited = this.groupOptions[0].value;
                }

            }).catch(() => {
                this.storeMessages.showMessageError("Failed to fetch user's groups.");
            });
        },
        getEditingEvent() {
            // set all variables
            ApiService.get(`events/event/${this.$route.params.uuid}/`)
            .then(res => {
                this.title = res.data.title;
                this.eventType = res.data.event_type;
                this.calendarType = res.data.event_calendar_type;
                this.length = res.data.event_length;

                let difference: number = 0;
                if (this.$route.name === "event_new") {
                    const currentDate = new Date();
                    currentDate.setHours(0, 0, 0, 0);
                    const firstDate = new Date(res.data.event_availability_options[0].start_date);
                    firstDate.setHours(0, 0, 0, 0);

                    // if the first date is in the past, add 7 days to the difference
                    if ((firstDate.getDay() === 0 ? 7 : firstDate.getDay()) <= (currentDate.getDay() === 0 ? 7 : currentDate.getDay())) {
                        if (this.calendarType === CalendarType.Date) {
                            difference = 7;
                        } else {
                            difference = 7 * 24;

                        }
                    }
                    currentDate.setDate(currentDate.getDate() - currentDate.getDay() + 1);
                    firstDate.setDate(firstDate.getDate() - firstDate.getDay() + 1);

                    const differenceInDays = Math.floor((currentDate.getTime() - firstDate.getTime()) / (1000 * 60 * 60 * 24));
                    if (this.calendarType === CalendarType.Date) {
                        difference += differenceInDays;
                    } else {
                        difference += differenceInDays * 24;
                    }
                }

                this.fromDate = initializeDateInput(CalendarType.Date,
                    addUnitsToDate(new Date(res.data.event_availability_options[0].start_date), this.calendarType!, difference).toString()
                )
                this.toDate = initializeDateInput(CalendarType.Date,
                    addUnitsToDate(new Date(res.data.event_availability_options[res.data.event_availability_options.length - 1].end_date), this.calendarType!, difference).toString()
                )

                this.description = res.data.description as string;
                this.deadline = initializeDateInput(CalendarType.DateHour,
                    addUnitsToDate(new Date(res.data.deadline), this.calendarType!, difference).toString()
                );

                this.groupInvited = res.data.invited_group?.id;
                this.isGroupOrganiser = res.data.is_group_organiser;

                this.selectedDateRanges = res.data.event_availability_options.map((dateRange: DateRange) => ({
                    start_date: addUnitsToDate(new Date(dateRange.start_date), this.calendarType!, difference),
                    end_date: addUnitsToDate(new Date(dateRange.end_date), this.calendarType!, difference),
                }));

                if (res.data.closed_group_members) {
                    this.closedGroupUsers = res.data.closed_group_members
                    .map((member: any) => ({
                        email: member.user.email,
                        exists: true,
                    }))
                    .filter((member: UserCreate) => member.email !== this.user?.email);
                }

                this.eventNotifications = {
                    afterCreation: res.data.event_notifications.some((notification: EventNotification) => notification.notification_type === EventNotificationType.Creation),
                    afterUpdate: res.data.event_notifications.some((notification: EventNotification) => notification.notification_type === EventNotificationType.Update),
                    beforeDeadline: res.data.event_notifications.some((notification: EventNotification) => notification.notification_type === EventNotificationType.Deadline),
                };
                this.eventNotificationsDeadline = initializeDateInput(CalendarType.DateHour, res.data.event_notifications.find((notification: EventNotification) => notification.notification_type === EventNotificationType.Deadline)?.notification_time);
            })
            .catch(() => {
                this.storeMessages.showMessageError("Failed to fetch event data.");
            });
        },

        // Closed group users
        addClosedGroupMember() {
            // // check email format
            if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(this.closedGroupUserEmail)) {
                this.closedGroupUserForceInvalidMessage = true;
                this.closedGroupMemberInvalidMessage = "Invalid email format";
                return;
            }

            // check duplicates
            if (this.closedGroupUsers.some(user => user.email === this.closedGroupUserEmail)) {
                this.closedGroupUserForceInvalidMessage = true;
                this.closedGroupMemberInvalidMessage = "This member is already added";
                return;
            }

            // can't add yourself
            if (this.closedGroupUserEmail === this.user?.email) {
                this.closedGroupUserForceInvalidMessage = true;
                this.closedGroupMemberInvalidMessage = "You can't add yourself to the group";
                return;
            }

            this.closedGroupUserForceInvalidMessage = false;
            this.closedGroupMemberInvalidMessage = "";

            ApiService.get(`/users/user/exists/${this.closedGroupUserEmail}/`).then((response: any) => {
                this.closedGroupUsers.push({
                    email: this.closedGroupUserEmail,
                    exists: response.data.exists,
                });
            }).catch(() => {
                this.storeMessages.showMessageError("Failed to add user to group");
            }).finally(() => {
                this.closedGroupUserEmail = "";
            });
        },
        deleteMember(user: UserCreate) {
            this.closedGroupUsers = this.closedGroupUsers.filter(u => u !== user);
        },
        async copyInviteLink() {
            navigator.clipboard.writeText(this.inviteLink);
            this.storeMessages.showMessage("Invite link copied to clipboard", 3000);
        },

        // helpers
        addUnitsToDate,
    },
    mounted() {
        this.getGroups();
        if (this.$route.params.uuid) {
            this.getEditingEvent();
        } else {
            this.calendarType = CalendarType.Date;
        }
    },
    watch: {
        calendarType(newType: CalendarType, oldType: CalendarType) {
            this.toDate = initializeDateInput(newType, this.toDate);
            this.fromDate = initializeDateInput(newType, this.fromDate);
            if (oldType)  // don't clean on mount
                this.selectedDateRanges = []
        },
    },
}
</script>
