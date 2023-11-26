import { CalendarType, DateRange } from "@/types/calendar";

function padNumber(number: number, places: number = 2): string {
    return number.toString().padStart(places, '0');
}

export function formatDateDayMonthYear(date: Date) {
    return `${date.getDate()}. ${date.getMonth() + 1}. ${date.getFullYear()}`;
}

export function formatDateDayMonth(date: Date) {
    return `${date.getDate()}. ${date.getMonth() + 1}.`;
}

export function formatDateDayMonthHour(date: Date) {
    return `${date.getDate()}. ${date.getMonth() + 1}. ${padNumber(date.getHours())}:${padNumber(date.getMinutes())}`;
}

export function formatDateHour(date: Date) {
    return `${padNumber(date.getHours())}:00`;
}

export function removeHoursMinutesFromDate(date: Date): Date {
    date.setHours(0, 0);
    return date;
}

export function formatDateForBackend(date: Date) {
    return `${date.getFullYear()}-${padNumber(date.getMonth() + 1)}-${padNumber(date.getDate())} ${padNumber(date.getHours())}:${padNumber(date.getMinutes())}:00`;
}

export function initializeDateInput(type: CalendarType, date?: string): string {    
    const now = date === undefined ? removeHoursMinutesFromDate(new Date()) : new Date(date);
    if (type === CalendarType.Date)
        return `${now.getFullYear()}-${padNumber(now.getMonth() + 1)}-${padNumber(now.getDate())}`;
    return `${now.getFullYear()}-${padNumber(now.getMonth() + 1)}-${padNumber(now.getDate())}T${padNumber(now.getHours())}:00`;
}

export function convertDateRangeForBackend(dateRange: DateRange): any {
    return {
        StartDate: formatDateForBackend(dateRange.from),
        EndDate: formatDateForBackend(dateRange.to),
    }
}

export function convertDateRangesForBackend(dateRanges: DateRange[]) {
    return dateRanges.map(convertDateRangeForBackend);
}

export function convertDateRangeFromBackend(dateRange: any): DateRange {
    return {
        from: new Date(dateRange.StartDate),
        to: new Date(dateRange.EndDate)
    } as DateRange
}

export function convertDateRangesFromBackend(dateRanges: any[]): DateRange[] {
    return dateRanges.map(convertDateRangeFromBackend);
}
