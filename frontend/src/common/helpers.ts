import { CalendarType, ICalendarDate, IDateRange } from "./interfaces";

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
    return `${padNumber(date.getHours())}:${padNumber(date.getMinutes())} ${date.getDate()}. ${date.getMonth() + 1}.`;
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

export function getSelectedDatesOnCalendar(selectedDates: ICalendarDate[]): IDateRange[] {
    const dates: any = [];
    let currentStart: Date|undefined = undefined;
    for (let i = 0; i < selectedDates.length; i++) {
        const currDate = selectedDates[i];
        if (currentStart === undefined && currDate.isAvailable)  // set currentStart
            currentStart = currDate.date;
        const prevDate = selectedDates[i - 1];
        if (currentStart !== undefined && i === selectedDates.length - 1) {
            if (currDate.isAvailable) {  // last one is available
                dates.push({
                    StartDate: formatDateForBackend(new Date(currentStart)),
                    EndDate: formatDateForBackend(new Date(currDate.date)),
                })
            } else {
                dates.push({
                    StartDate: formatDateForBackend(new Date(currentStart)),
                    EndDate: formatDateForBackend(new Date(prevDate.date)),
                })
            }
        }
        else if (currentStart !== undefined && !currDate.isAvailable) {  // add prevDate to dates
            dates.push({
                StartDate: formatDateForBackend(new Date(currentStart)),
                EndDate: formatDateForBackend(new Date(prevDate.date)),
            })
            currentStart = undefined;
        }
    }
    return dates;
}
