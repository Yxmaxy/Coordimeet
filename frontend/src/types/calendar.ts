export interface DateRange {
    from: Date,
    to: Date,
}

export interface CalendarDate {
    display: string,
    date: Date,
    isInRange: boolean,
    isAvailable: boolean,
}

export enum CalendarType {
    DateTime = 0,
    Date = 1,
}

export enum CalendarMode {
    Create = 0,
    Select = 1,
    Disabled = 2,
}
