export interface DateRange {
    start_date: Date,
    end_date: Date,
}

export enum CalendarType {
    Date = 1,
    DateHour = 2,
}

export interface CalendarDate {
    date: Date,
    heatmap: number,  // number of "hits"
}
