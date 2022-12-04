// Calendar date range
export interface IDateRange {
    from: Date,
    to: Date,
}

// Single calendar date
export interface ICalendarDate {
    display: string,
    date: Date,
    isInRange: boolean,
    isAvailable?: boolean,
}

// Calendar type
export enum CalendarType {
    Date = 0,
    DateTime = 1,
}