import { CalendarType } from "./interfaces";

function padNumber(number: number, places: number = 2): string {
    return number.toString().padStart(places, '0');
}

export function formatDateDayMonth(date: Date) {
    return `${date.getDate()}. ${date.getMonth() + 1}.`;
}

export function formatDateHour(date: Date) {
    return `${padNumber(date.getHours())}:00`;
}

export function removeHoursMinutesFromDate(date: Date): Date {
    date.setHours(0, 0);
    return date;
}

export function initializeDateInput(type: CalendarType): string {
    const now = removeHoursMinutesFromDate(new Date());
    if (type === CalendarType.Date)
        return `${now.getFullYear()}-${padNumber(now.getMonth() + 1)}-${padNumber(now.getDate())}`;
    return `${now.getFullYear()}-${padNumber(now.getMonth() + 1)}-${padNumber(now.getDate())}T${padNumber(now.getHours())}:00`;
}