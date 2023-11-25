import { CalendarType, DateRange } from "@/types/calendar";
import { User } from "@/types/user";

export interface Event {
    IDEvent: number,
    CalendarType: CalendarType,
    Config: Object,
    EventDates: DateRange[],
    Length: number,
    Name: string,
    Deadline: string,
    Organizer: User,
    UrlJoinLink: string,
    SelectedDate: string|null,
}

export enum EventPageType {
    NonConfirmed = 0,   // invitee sees just basic event data, confirm decline button
    Invitee = 1,        // calendar and all event data
    Organizer = 2,      // data about user responses, ending data
    Finished = 3,       // Event has finished, show only the simplest information
}
