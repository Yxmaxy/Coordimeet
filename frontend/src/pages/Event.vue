<template>
    <div class="bg-main-000 h-full">
        <!-- NotLoggedIn -->
        <div
            v-if="pageTypeIn(EventPageType.NotLoggedIn) && eventData"
            class="flex justify-center items-center min-h-[calc(100vh-3.5rem)]"
        >
            <div class="bg-main-100 px-16 py-10 rounded-lg shadow-lg">
                <div class="text-xl font-bold">You've been invited to:</div>
                <div class="text-2xl font-bold">{{ eventData.title }}</div>
                <div class="mt-3">
                    It seems like you are not logged in. You can choose to:
                    <ul>
                        <li class="ml-5 list-disc">Decline the invitation</li>
                        <li class="ml-5 list-disc">Log in or Sign up</li>
                        <li class="ml-5 list-disc">
                            <div class="flex items-center gap-1.5">
                                Submit anonymously
                                <help-icon>
                                    If you choose to submit an anonymous response, a temporary account will be created for you.
                                    <br />
                                    If you try to access the same event from another browser or if you log out, you will not be able to see your previous response.
                                </help-icon>
                            </div>
                        </li>
                    </ul>
                </div>
                <div class="flex justify-center gap-4 mt-4">
                    <custom-button @click="() => $router.push('/')">Decline</custom-button>
                    <custom-button @click="onLoginOrSignup">Log in or Sign up</custom-button>
                    <custom-button @click="onSubmitAnon">Submit anonymously</custom-button>
                </div>
            </div>
        </div>

        <!-- NonConfirmed and Finished -->
        <div
            v-else-if="pageTypeIn(EventPageType.NonConfirmed, EventPageType.Finished)"
            class="flex justify-center items-center min-h-[calc(100vh-3.5rem)]"
        >
            <event-data
                v-if="eventData"
                class="bg-main-100 px-16 py-10 rounded-lg shadow-lg"
                :event="eventData"
            >
                <template v-slot:before>
                    <div class="text-xl font-bold">
                        <template v-if="pageTypeIn(EventPageType.NonConfirmed)">
                            You've been invited to:
                        </template>
                        <template v-else>
                            This event's date has been selected:
                        </template>
                    </div>
                </template>
                <template v-slot:after>
                    <div
                        v-if="pageTypeIn(EventPageType.NonConfirmed)"
                        class="flex justify-center gap-4 mt-4"
                    >
                        <custom-button
                            :negative="true"
                            :click="declineInvitation"
                        >
                            Decline
                        </custom-button>
                        <custom-button
                            :click="() => eventPageType = EventPageType.Invitee"
                        >
                            Accept
                        </custom-button>
                    </div>
                    <div
                        v-if="pageTypeIn(EventPageType.Finished)"
                        class="text-lg font-bold mt-4"
                    >
                        The selected date is: {{ formatDateRange({ start_date: eventData.selected_start_date!, end_date: eventData.selected_end_date! }, eventData?.event_calendar_type) }}

                        <div class="flex justify-center">
                            <custom-button
                                class="mt-4"
                                :click="getICalFile"
                                :small="true"
                            >
                                Download iCal file
                                <custom-icon class="text-base" icon="download" />
                            </custom-button>
                        </div>
                    </div>
                </template>
            </event-data>
            <a ref="icalDownload" class="hidden" :href="icalFileUrl" download="event.ics"></a>
        </div>

        <!-- FinishConfirm -->
        <div
            v-if="showFinishConfirm && eventData"
            class="flex justify-center items-center min-h-[calc(100vh-3.5rem)]"
        >
            <div class="bg-main-100 px-16 py-10 rounded-lg shadow-lg">
                <div class="text-xl font-bold">Are you sure you want to finish this event?</div>
                <div class="text-2xl font-bold">Your choice: {{ formatDateRange(selectedDateRanges[0], eventData?.event_calendar_type) }}</div>
                <div class="mt-3">
                    <div>
                        This action is irreversible.
                        <br/>
                        You will not be able to change the date after you finish the event.
                    </div>
                    <div class="mt-3">
                        You can send the next notifications:
                        <div class="ml-3 flex flex-col gap-2">
                            <custom-toggle
                                class="mt-2"
                                v-model="eventNotifications.afterEventDateSelected"
                            >
                                <template v-slot:right>
                                    <div class="ml-2 flex gap-1 items-center">
                                        <div>after the event date is selected</div>
                                    </div>
                                </template>
                            </custom-toggle>

                            <div class="flex flex-col gap-1">
                                <custom-toggle
                                    v-model="eventNotifications.beforeEventStarts"
                                >
                                    <template v-slot:right>
                                        <div class="ml-2 flex gap-1 items-center">
                                            <div>before the event starts</div>
                                        </div>
                                    </template>
                                </custom-toggle>
                                <label
                                    v-if="eventNotifications.beforeEventStarts"
                                    class="ml-8"
                                >
                                    <custom-input
                                        type="datetime-local"
                                        v-model="eventNotificationsBeforeStarts"
                                        :required="eventNotifications.beforeEventStarts"
                                    />
                                </label>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="flex justify-center gap-4 mt-4">
                    <custom-button :click="() => showFinishConfirm = false">Cancel</custom-button>
                    <custom-button :click="finishEvent">Finish this event!</custom-button>
                </div>
            </div>
        </div>

        <!-- Content -->
        <tab-controller
            v-else
            :tabs="tabs"
            :breakpoint="tabControllerBreakpoint"
        >
            <template v-slot:event>
                <div class="h-full bg-main-100 p-4">
                    <event-data
                        v-if="eventData"
                        :event="eventData"
                    >
                        <template v-slot:after>
                            <custom-button
                                v-if="pageTypeIn(EventPageType.Organiser)"
                                class="mt-5"
                                :small="true"
                                @click="copyLink"
                            >
                                Copy invite link to clipboard <custom-icon class="text-base" icon="person_add" />
                            </custom-button>
                        </template>
                    </event-data>
                </div>
            </template>

            <template v-slot:responses>
                <div
                    v-for="participant in eventParticipants"
                    :class="[{
                        'text-main-200': !participant.isSelected,
                        'hover:bg-main-100 cursor-pointer': isOrganiserMode,
                    },
                    'select-none p-[1.1rem] font-bold border-b-2 border-b-main-200 transition-colors',
                    'flex justify-between items-center']"
                    @click="toggleParticipant(participant)"
                >
                    {{ participant.user.email }}
                    <custom-icon v-if="participant.not_comming" icon="event_busy"/>
                    <custom-icon v-if="!participant.not_comming" icon="event_available"/>
                </div>
            </template>

            <template v-slot:date_choices>
                <div
                    v-for="dateRange in getBestDateRanges"
                    :class="[{
                        'hover:bg-main-100 cursor-pointer': isOrganiserMode,
                    }, 'select-none p-[1.1rem] font-bold border-b-2 border-b-main-200 transition-colors',
                    'flex justify-between items-center']"
                    @click="() => onOrganiserDateChoiceSelect(dateRange.range)"
                >
                    <div v-if="eventData?.event_calendar_type">
                        {{ formatDateRange(dateRange.range, eventData?.event_calendar_type, false) }}
                    </div>
                    <div>{{ dateRange.hits }}</div>
                </div>
            </template>

            <template v-slot:calendar>
                <div class="bg-main-100 shadow-md p-3 mb-3">
                    <div class="flex justify-between items-baseline">
                        <!-- Organiser mode toggle -->
                        <div>
                            <custom-toggle
                                v-if="pageTypeIn(EventPageType.Organiser)"
                                v-model="isOrganiserMode"
                            >
                                <template v-slot:left>
                                    <span class="flex items-center gap-1 font-bold mr-1">
                                        Invitee <custom-icon class="text-base" icon="person" />
                                    </span>
                                </template>
                                <template v-slot:right>
                                    <span class="flex items-center gap-1 font-bold ml-1">
                                        Organiser <custom-icon class="text-base" icon="engineering" />
                                    </span>
                                </template>
                            </custom-toggle>
                        </div>
    
                        <!-- Submit buttons -->
                        <div class="flex flex-wrap justify-end gap-2">
                            <div v-if="storeOnline.isOnline">
                                <custom-button
                                    v-if="pageTypeIn(EventPageType.Organiser) && isOrganiserMode"
                                    :small="true"
                                    :disabled="!isSelectedDateRangesSet || selectedDateRanges.length !== 1"
                                    :click="() => showFinishConfirm = true"
                                >
                                    Submit and finish <custom-icon class="text-base" icon="event_available" />
                                </custom-button>
                                <custom-button
                                    v-else
                                    :small="true"
                                    :click="submitSelection"
                                    :disabled="gettingParticipantData"
                                >
                                    <template v-if="!isSelectedDateRangesSet">
                                        Submit as unavailable
                                    </template>
                                    <template v-else>
                                        Submit
                                    </template>
                                    <custom-icon class="text-base" icon="event" />
                                </custom-button>
                            </div>
                            <div v-if="!isOrganiserMode">
                                <custom-button :small="true" :click="() => ($refs.icalFileInput as HTMLInputElement).click()">
                                    Upload iCal file <custom-icon class="text-base" icon="upload" />
                                </custom-button>
                                <input
                                    ref="icalFileInput"
                                    type="file"
                                    accept=".ics"
                                    @change="getUnavailableDatesFromICal"
                                    class="hidden"
                                />
                            </div>
                        </div>
                    </div>
                </div>
                <!-- Calendar -->
                <calendar
                    v-if="eventData"
                    v-model:selectedDateRanges="selectedDateRanges"
                    :roughEventDateRange="roughEventDateRange"
                    :selectableDateRanges="eventData.event_availability_options"
                    :heatmapDateRanges="isOrganiserMode ? selectedEventParticipantDateRanges : []"
                    :calendarType="eventData.event_calendar_type"
                    :enableOptions="!isOrganiserMode"
                />
            </template>
        </tab-controller>
    </div>
</template>

<script lang="ts">
import { AxiosResponse } from "axios";

import ApiService from "@/utils/ApiService";
import { useStoreUser } from "@/stores/storeUser";
import { useStoreMessages } from "@/stores/storeMessages";
import { useStoreOnline } from "@/stores/storeOnline";

import { CalendarType, DateRange } from "@/types/calendar";
import { Event, EventNotification, EventNotificationType, EventPageType, EventParticipant } from "@/types/event";
import { Tab } from "@/types/tabs";
import { Member, Role } from "@/types/user";
import { initializeDateInput, formatDateRange, addUnitsToDate } from "@/utils/dates";

import EventData from "@/components/EventData.vue";
import Calendar from "@/components/Calendar.vue";
import TabController from "@/components/TabController.vue";
import CustomButton from "@/components/ui/CustomButton.vue";
import CustomToggle from "@/components/ui/CustomToggle.vue";
import CustomIcon from "@/components/ui/CustomIcon.vue";
import CustomInput from "@/components/ui/CustomInput.vue";
import HelpIcon from "@/components/ui/HelpIcon.vue";

interface DateChoice {
    range: DateRange;
    hits: number;
}

export default {
    components: {
        Calendar,
        TabController,
        EventData,
        CustomButton,
        CustomToggle,
        CustomIcon,
        CustomInput,
        HelpIcon,
    },
    setup() {
        const storeUser = useStoreUser();
        const storeMessages = useStoreMessages();
        const storeOnline = useStoreOnline();

        return {
            storeUser,
            storeMessages,
            storeOnline,

            EventPageType,
            CalendarType,
        }
    },
    data() {
        return {
            eventData: null as null|Event,
            eventPageType: EventPageType.NonConfirmed as EventPageType,
            eventParticipants: [] as EventParticipant[],

            selectedDateRanges: [] as DateRange[],  // the current calendar selection
            previousSelectedDateRanges: [] as DateRange[],  // set if the invitee submitted before

            isOrganiserMode: false,  // organiser mode toggle
            gettingParticipantData: false,  // for fetching event participants

            showFinishConfirm: false,  // show finish confirm dialog
            icalFileUrl: "",  // ical file url

            tabs: [] as Tab[],
            tabControllerBreakpoint: 750,

            eventNotifications: {
                afterEventDateSelected: false,
                beforeEventStarts: false,
            },
            eventNotificationsBeforeStarts: initializeDateInput(CalendarType.DateHour),
        }
    },
    computed: {
        roughEventDateRange(): DateRange {
            if (this.eventData === null)
                return {} as DateRange
            return {
                start_date: new Date(this.eventData.event_availability_options.reduce(
                    (prev, min) => prev.start_date < min.start_date ? prev : min).start_date
                ),
                end_date: new Date(this.eventData.event_availability_options.reduce(
                    (prev, max) => prev.end_date > max.end_date ? prev : max).end_date
                ),
            }
        },
        isSelectedDateRangesSet(): boolean {
            return this.selectedDateRanges.length !== 0
        },
        selectedEventParticipantDateRanges(): DateRange[] {
            if (!this.eventParticipants)  // TODO: add check that the user is and admin or organiser
                return [];
            const participantDates = this.eventParticipants
                .filter(participant => participant.isSelected)
                .flatMap((participant: EventParticipant) => 
                    participant.participant_availabilities.map(availability => ({
                        start_date: new Date(availability.start_date),
                        end_date: new Date(availability.end_date),
                    }))
                ) as DateRange[];
            return participantDates;
        },
        getBestDateRanges(): DateChoice[] {
            // Loop through all date ranges in selectedEventParticipantDateRanges.
            // Move through each date range by using the addUnitsToDate helper
            // The calendarType parameter is provided by eventData.event_calendar_type
            // Add each unit to a map with the number of times it appears.

            if (this.eventData === null)  // TODO: add check that the user is and admin or organiser
                return []

            // create a map for each possible date with the number of "hits"
            const dateCountMap = new Map<string, number>();
            const calendarType = this.eventData.event_calendar_type;

            this.selectedEventParticipantDateRanges.forEach(range => {
                let currentDate = new Date(range.start_date);
                const endDate = new Date(range.end_date);

                while (currentDate <= endDate) {
                    const dateString = currentDate.toISOString();
                    dateCountMap.set(dateString, (dateCountMap.get(dateString) || 0) + 1);
                    currentDate = this.addUnitsToDate(currentDate, calendarType, 1);
                }
            });

            // Loop through ordered keys of dateCountMap.
            // Use the sliding window method to calculate the number of "hits" for each date range.
            // A single date range is this.eventData.length long and is not related to user's date ranges
            const result = [] as DateChoice[];
            const dateCountKeys = Array.from(dateCountMap.keys()).sort();

            for (const startDate of dateCountKeys) {
                const endDate = this.addUnitsToDate(new Date(startDate), this.eventData.event_calendar_type, this.eventData.event_length);
                // Check if endDate is in dateCountKeys
                if (!dateCountKeys.includes(this.addUnitsToDate(new Date(endDate), this.eventData.event_calendar_type, -1).toISOString())) {
                    continue;
                }
                // sum all hits that fall between the start and end date
                let hits = 0;
                for (let currentDate = new Date(startDate); currentDate < endDate; currentDate = this.addUnitsToDate(currentDate, calendarType, 1)) {
                    hits += dateCountMap.get(currentDate.toISOString()) || 0;
                }
                result.push({
                    range: {
                        start_date: new Date(startDate),
                        end_date: endDate,
                    },
                    hits,
                });
            }

            // order the result by hits
            return result.sort((a, b) => b.hits - a.hits);
        },
    },
    methods: {
        // event
        getEventData() {
            // gets the event data and sets page type
            ApiService.get(`events/event/${this.$route.params.uuid}/`)
            .then(res => {
                // parse all dates
                const parseDate = (date: string) => new Date(date);
                const parseDateNull = (date: string) => date ? parseDate(date) : null;
                
                const eventData = {
                    ...res.data,
                    deadline: parseDate(res.data.deadline),
                    selected_start_date: parseDateNull(res.data.selected_start_date),
                    selected_end_date: parseDateNull(res.data.selected_end_date),
                    event_availability_options: res.data.event_availability_options.map(
                        (dateRange: any) => ({
                            start_date: parseDate(dateRange.start_date),
                            end_date: parseDate(dateRange.end_date),
                        })
                    ),
                } as Event;

                // the event has finished
                if (eventData.selected_start_date !== null) {
                    this.eventPageType = EventPageType.Finished;
                // the current user is the organiser or in the organiser group as admin or owner
                } else if (
                    this.storeUser.user?.id === eventData.organiser?.id ||
                    (
                        eventData.is_group_organiser
                        && eventData.invited_group?.members.some(
                            (member: Member) => member.user?.id === this.storeUser.user?.id && [Role.OWNER, Role.ADMIN].includes(member.role))
                        )
                ) {
                    this.eventPageType = EventPageType.Organiser;
                    this.getParticipants();
                    this.tabControllerBreakpoint = 1382;
                    this.tabs =  [
                        {
                            name: "Event",
                            slot_name: "event",
                            narrow: "sm",
                            icon: "description",
                        },
                        {
                            name: "Responses",
                            slot_name: "responses",
                            narrow: "sm",
                            icon: "group",
                        },
                        {
                            name: "Date choices",
                            slot_name: "date_choices",
                            narrow: "sm",
                            icon: "calendar_clock",
                        },
                        {
                            name: "Calendar",
                            slot_name: "calendar",
                            icon: "calendar_today",
                        },
                    ]
                } else {
                    this.tabs =  [
                        {
                            name: "Event",
                            slot_name: "event",
                            narrow: "sm",
                            icon: "description",
                        },
                        {
                            name: "Calendar",
                            slot_name: "calendar",
                            icon: "calendar_today",
                        },
                    ]
                }
                this.eventData = eventData;
            }).catch(() => {
                this.storeMessages.showMessageError("You don't have permissions to access this event!");
                this.$router.push("/event/list");
            });
        },
        getPreviousSelectedDateRanges() {
            // gets the user's selected date ranges if they exist
            // also "upgrades" the user to invitee if needed
            ApiService.get(`/events/event/participants/${this.$route.params.uuid}/`)
                .then((response: AxiosResponse) => {
                    if (response.data.error) {
                        this.storeMessages.showMessageError(`An error occured while fetching your previous selection: ${response.data.error}`)
                        return;
                    }

                    if (response.data.participant_availabilities.length !== 0 || response.data.not_comming) {
                        // "upgrade" user to invitee if the data was submitted
                        if (this.eventPageType === EventPageType.NonConfirmed)
                            this.eventPageType = EventPageType.Invitee;

                        // update selectedDateRanges with previous response
                        this.previousSelectedDateRanges = response.data.participant_availabilities.map((range: DateRange) => ({
                            start_date: new Date(range.start_date),
                            end_date: new Date(range.end_date),
                        }));

                        // intialize the selected date ranges
                        this.selectedDateRanges = this.previousSelectedDateRanges;
                    }
                });
        },
        getParticipants() {
            this.gettingParticipantData = true;
            ApiService.get(`/events/event/organiser/${this.$route.params.uuid}/`)
                .then(res => {
                    if (res.data.error) {
                        this.storeMessages.showMessageError(`An error occured while fetching the participants: ${res.data.error}`)
                        return;
                    }
                    if (res.data.length === 0)
                        return;

                    // set the participants array
                    this.eventParticipants = res.data.map((participant: any) => {
                        return {
                            ...participant,
                            isSelected: true,
                        } as EventParticipant
                    })
                }).finally(() => {
                    this.gettingParticipantData = false;
                })
        },
        async getUnavailableDatesFromICal(event: any) {
            const file = event.target.files[0];
            const formData = new FormData();
            formData.append("file", file);

            const res = await ApiService.post(`events/event/icalendar/${this.$route.params.uuid}/`, formData)
            // handle the response
            const unavailableDates = res.data.map((range: any) => ({
                start_date: new Date(range.event_start),
                end_date: new Date(range.event_end),
            } as DateRange));

            let newSelectedDateRanges = this.eventData?.event_availability_options!.map((availabilityOption: any) => (
                {
                    start_date: new Date(availabilityOption.start_date),
                    end_date: new Date(availabilityOption.end_date),
                } as DateRange
            ));
            for (const range of unavailableDates) {
                newSelectedDateRanges = this.deleteDateRangeFromDateRanges(range, newSelectedDateRanges!);
            }
            if (!newSelectedDateRanges) {
                return;
            }
            this.selectedDateRanges = newSelectedDateRanges;
        },
        getICalFile() {
            ApiService.get(`events/event/icalendar/${this.$route.params.uuid}/`, { responseType: "blob" })
                .then(res => {
                    // handle the response
                    const url = window.URL.createObjectURL(new Blob([res.data]));
                    this.icalFileUrl = url;
                    this.$nextTick(() => {
                        (this.$refs.icalDownload as HTMLAnchorElement).click();
                    });
                });
        },

        // submit event
        submitSelection() {
            // submit as an invitee
            const data = !this.isSelectedDateRangesSet ? {not_comming: true} : {
                participant_availabilities: this.selectedDateRanges.map(range => ({
                    start_date: range.start_date.toISOString(),
                    end_date: range.end_date.toISOString(),
                }))
            }

            // handler if the event succeedes
            ApiService.post(`/events/event/participants/${this.$route.params.uuid}/`, data)
                .then((response: AxiosResponse) => {
                    if (response.status !== 200)
                        return;
                    this.previousSelectedDateRanges = this.selectedDateRanges;
                    this.storeMessages.showMessage("Your response has been submitted");
                    if (this.storeUser.user!.id === this.eventData?.organiser?.id)
                        this.getParticipants();
                })
            
        },
        finishEvent() {
            // if eventNotifications.beforeEventStarts is set, check that the notification time is before
            // the selected start date
            if (this.eventNotifications.beforeEventStarts) {
                const notificationTime = new Date(this.eventNotificationsBeforeStarts);
                if (notificationTime >= this.selectedDateRanges[0].start_date) {
                    this.storeMessages.showMessageError("The notification time must be before the event starts!");
                    return;
                }
            }

            // validate selected date
            if (!this.isSelectedDateRangesSet || this.selectedDateRanges.length !== 1) {
                this.storeMessages.showMessageError("You did not select a date range!");
                return;
            }

            // check that the selected date range is the same length as the eventData.event_length
            const selectedDateRange = this.selectedDateRanges[0];
            let startDate = new Date(selectedDateRange.start_date);
            let units = 1;
            while (startDate.getTime() < selectedDateRange.end_date.getTime()) {
                startDate = this.addUnitsToDate(new Date(startDate), this.eventData?.event_calendar_type!, 1);
                units++;
            }
            if (units !== this.eventData!.event_length) {
                this.storeMessages.showMessageError(`You did not select a valid date range. The event must be exactly ${this.eventData!.event_length} ${this.eventData!.event_calendar_type === CalendarType.Date ? "days" : "hours"} long!`);
                return;
            }

            const eventNotifications = [] as EventNotification[]
            if (this.eventNotifications.afterEventDateSelected)
                eventNotifications.push({ notification_type: EventNotificationType.EventDateSelected });
            if (this.eventNotifications.beforeEventStarts)
                eventNotifications.push({
                    notification_type: EventNotificationType.EventStart,
                    notification_time: new Date(this.eventNotificationsBeforeStarts),
                });
            
            let endDate = selectedDateRange.end_date;
            if (this.eventData!.event_calendar_type == CalendarType.DateHour) {
                endDate = this.addUnitsToDate(selectedDateRange.end_date, CalendarType.DateHour, 1);
            }
            
            const data = {
                selected_start_date: selectedDateRange.start_date,
                selected_end_date: endDate,
                event_notifications: eventNotifications,
            }

            ApiService.post(`/events/event/organiser/${this.$route.params.uuid}/`, data)
                .then(() => {
                    this.storeMessages.showMessage("The event date was successfully selected!");
                    this.$router.push("/event/list");
                })
        },
        declineInvitation() {
            ApiService.post(`/events/event/participants/${this.$route.params.uuid}/`, {not_comming: true})
            .then((response: AxiosResponse) => {
                if (response.status !== 200)
                    return;
                this.storeMessages.showMessage("You have declined the invitation");
                this.$router.push("/event/list");
            })
        },

        // interaction
        toggleParticipant(participant: EventParticipant) {
            if (!this.isOrganiserMode)
                return;
            participant.isSelected = !participant.isSelected;
        },
        onOrganiserDateChoiceSelect(dateRange: DateRange) {
            if (!this.isOrganiserMode)
                return;
            this.selectedDateRanges = [{
                start_date: new Date(dateRange.start_date),
                end_date: new Date(this.addUnitsToDate(new Date(dateRange.end_date), this.eventData!.event_calendar_type, -1)),
            }];
        },
        deleteDateRangeFromDateRanges(deleteDateRange: DateRange, dateRanges: DateRange[]): DateRange[] {
            // remove "eaten up" ranges
            dateRanges = dateRanges.filter(x => {
                return !(x.start_date >= deleteDateRange.start_date && x.end_date <= deleteDateRange.end_date);
            });
            
            for (const dateRange of dateRanges) {
                if (dateRange.start_date <= deleteDateRange.start_date && deleteDateRange.end_date <= dateRange.end_date) {
                    // selection splits existing range
                    if (deleteDateRange.start_date > dateRange.start_date && deleteDateRange.end_date < dateRange.end_date) {
                        // add current selection to date range
                        const newDateFrom = new Date(deleteDateRange.start_date);
                        const newDateTo = new Date(deleteDateRange.end_date);
                        // add padding
                        this.addUnitsToDate(newDateFrom, this.eventData?.event_calendar_type!, -1);
                        this.addUnitsToDate(newDateTo, this.eventData?.event_calendar_type!, 1);

                        // create new date range for last part
                        dateRanges.push({
                            start_date: newDateTo,
                            end_date: dateRange.end_date,
                        });
                        // update current range for first part
                        dateRange.end_date = new Date(newDateFrom);
                        continue;
                    }
                    // remove from start
                    if (deleteDateRange.start_date.getTime() === dateRange.start_date.getTime()) {
                        const newDateTo = new Date(deleteDateRange.end_date);
                        // add padding
                        this.addUnitsToDate(newDateTo, this.eventData?.event_calendar_type!, 1)

                        dateRange.start_date = newDateTo;
                    }
                    // remove from end
                    if (deleteDateRange.end_date.getTime() === dateRange.end_date.getTime()) {
                        const newDateFrom = new Date(deleteDateRange.start_date);
                        // add padding
                        this.addUnitsToDate(newDateFrom, this.eventData?.event_calendar_type!, -1)

                        dateRange.end_date = newDateFrom;
                    }
                }
            }
            return dateRanges;
        },

        // helpers
        pageTypeIn(...types: EventPageType[]): boolean {
            return types.includes(this.eventPageType);
        },
        copyLink() {
            navigator.clipboard.writeText(`${import.meta.env.VITE_FRONTEND_URL}/event/${this.$route.params.uuid}`);
            this.storeMessages.showMessage("Link copied to clipboard", 1000);
        },
        onShowFinishConfirm() {
            this.eventNotificationsBeforeStarts = initializeDateInput(this.eventData?.event_calendar_type!, this.selectedDateRanges[0]?.start_date.toISOString());
            this.showFinishConfirm = true;
        },

        // not logged in actions
        onLoginOrSignup() {
            this.storeUser.redirectAfterLogin = this.$route.fullPath;
            this.$router.push({"name": "login"});
        },
        onSubmitAnon() {
            this.storeUser.onCreateAnonymousUser()
                .then(() => {
                    this.storeMessages.showMessage("You have been logged in as an anonymous user");
                    this.eventPageType = EventPageType.Invitee;
                });
        },
        formatDateRange,
        addUnitsToDate,
    },
    mounted() {
        this.getEventData();
        if (!this.storeUser.user) {
            this.eventPageType = EventPageType.NotLoggedIn;
        } else {
            this.getPreviousSelectedDateRanges();
        }

    },
    watch: {
        isOrganiserMode(isOrganiser: boolean) {
            if (isOrganiser) {
                // get participant data
                this.getParticipants();
                this.selectedDateRanges = [];
            } else {
                // initialize invitee selection to previous selection
                this.selectedDateRanges = this.previousSelectedDateRanges;
                this.eventParticipants.map(participant => participant.isSelected = true);
            }
        },
    }
}
</script>
