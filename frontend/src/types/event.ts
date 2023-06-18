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
    Invitee = 0,        // calendar and all event data
    Organizer = 1,      // data about user responses, ending data
    NonConfirmed = 2,   // invitee sees just basic event data, confirm decline button
    Finished = 3,       // Event has finished, show only the simplest information
}
