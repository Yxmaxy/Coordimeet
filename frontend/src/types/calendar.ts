export interface DateRange {
    start_date: Date,
    end_date: Date,
}

export enum CalendarType {
    DateHour = 0,
    Date = 1,
}

export interface CalendarDate {
    date: Date,
    heatmap: number,  // number of "hits"
}
