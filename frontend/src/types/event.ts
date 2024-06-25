import { CalendarType, DateRange } from "@/types/calendar";
import { User, Group } from "@/types/user";

export enum EventType {
    Public = 1,
    Group = 2,
    Closed = 3,
}

export interface EventAvailabilityOption extends DateRange {
    pk?: number,
    event?: Event,
}

export enum EventNotificationType {
    Creation = 1,
    Update = 2,
    BeforeDeadline = 3,
    EventDateSelected = 4,
    EventStart = 5,
    Deadline = 6,
}

export interface EventNotification {
    pk?: number,
    uuid?: string,
    notification_type: EventNotificationType,
    notification_time?: Date,
}

export interface Event {
    pk?: number,

    title: string,
    event_uuid?: string,
    event_calendar_type: CalendarType,
    event_type: EventType,

    organiser?: User,
    invited_group?: Group,
    is_group_organiser: boolean,

    description?: string,
    event_length: number,
    deadline: Date,

    selected_start_date: Date | null,
    selected_end_date: Date | null,

    created_at: Date,
    updated_at: Date,

    event_availability_options: EventAvailabilityOption[],
    event_notifications: EventNotification[],

    closed_group_users?: User[],

    user_response?: boolean|null,
}

export enum EventPageType {
    NotLoggedIn = -1,   // user is not logged in - prompt to log in or use anonymous account
    NonConfirmed = 0,   // invitee sees just basic event data, confirm decline button
    Invitee = 1,        // calendar and all event data
    Organiser = 2,      // data about user responses, ending data
    Finished = 3,       // Event has finished, show only the simplest information
}

export interface EventParticipant {
    user: User,
    not_comming: boolean,
    participant_availabilities: DateRange[],

    isSelected: boolean,
}
