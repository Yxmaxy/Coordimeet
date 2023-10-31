<template>
    <div>
        <div v-for="dateRange in selectedDateRanges">
            {{ formatDateDayMonthYear(dateRange.from) }} - {{ formatDateDayMonthYear(dateRange.to) }}
        </div>
        <!-- Header -->
        <div>
            <button @click="prevWeek">Prev</button>
            <button @click="nextWeek">Next</button>

            <div>Selected week {{ selectedWeek }}</div>
        </div>

        <!-- Calendar -->
        <div :class="[{
            'grid-cols-7': calendarType === CalendarType.Date,
            'grid-flow-col grid-rows-24': calendarType === CalendarType.DateTime,
        }, 'grid gap-0.5']">
            <!-- A date element -->
            <div
                v-for="date in getCalendarDates"
                :class="[{
                    'bg-calendar-available': isDateInSelectedDateRanges(date),
                }, 'bg-calendar-in-range p-2 select-none cursor-pointer']"
                @mousedown="onDateMouseDown(date)"
                @mouseup="onDateMouseUp(date)"
            >
                {{ dateDisplayFunction(date) }}
            </div>
        </div>
    </div>
</template>

<script lang="ts">
import { PropType } from "vue";

import { formatDateDayMonthYear, formatDateDayMonth, formatDateDayMonthHour, formatDateHour, formatDateForBackend } from "@/utils/dates";
import { CalendarType, CalendarDate, DateRange, CalendarMode } from "@/types/calendar";

export default {
    name: "Calendar2",
    setup() {
        return {
            CalendarType,
        }
    },
    props: {
        // rough event duration for calculating pages
        roughEventDateRange: {
            type: Object as PropType<DateRange>,
            required: true,
        },
        // calendar type
        calendarType: {
            type: Number as PropType<CalendarType>,
            required: true,
        },
    },
    data() {
        return {
            selectedDateRanges: [] as DateRange[],  // date ranges in green

            fromDate: null as null | Date,  // set on from date select
            fromMode: "add" as "add" | "delete",  // mode when selecting from date

            selectedWeek: 0,  // current selected week
        }
    },
    computed: {
        // gets dates to display on the calendar
        getCalendarDates(): Date[] {
            if (!this.roughEventDateRange)
                return [];
            const dates: Date[] = [];
            const datePadding = 7;  // how many days to add to the calendar
            const datesLimit = this.calendarType === CalendarType.Date ? 371 : 24 * 7;
            
            const rangeConversion = {
                [CalendarType.Date]: {
                    from: (date: Date) => {
                        // get current day of the week (0-6)
                        const currentDayOfWeek = date.getDay();
                        // get first day of the week (Monday)
                        const newDate = new Date(date.setDate(
                            date.getDate() - (currentDayOfWeek === 0 ? 6 : currentDayOfWeek - 1)));
                        newDate.setDate(newDate.getDate() - datePadding);
                        return newDate;
                    },
                    to: (date: Date) => {
                        // get current day of the week (0-6)
                        const currentDayOfWeek = date.getDay();
                        // get last day of the week (Sunday)
                        const newDate = new Date(date.setDate(
                            date.getDate() + (currentDayOfWeek === 0 ? 0 : 7 - currentDayOfWeek)));
                        newDate.setDate(newDate.getDate() + datePadding);
                        return newDate;
                    },
                },
                [CalendarType.DateTime]: {
                    from: (date: Date) => {
                        // get current day of the week (0-6)
                        const currentDayOfWeek = date.getDay();
                        // get first day of the week (Monday)
                        const newDate = new Date(date.setDate(
                            date.getDate() - (currentDayOfWeek === 0 ? 6 : currentDayOfWeek - 1)));
                        newDate.setDate(newDate.getDate() + this.selectedWeek * 7);
                        newDate.setHours(0, 0);
                        return newDate;
                    },
                    to: (date: Date) => {
                        // get current day of the week (0-6)
                        const currentDayOfWeek = date.getDay();
                        // get last day of the week (Sunday)
                        const newDate = new Date(date.setDate(
                            date.getDate() + (currentDayOfWeek === 0 ? 0 : 7 - currentDayOfWeek)));
                        newDate.setDate(newDate.getDate() + this.selectedWeek * 7);
                        newDate.setHours(23, 59);
                        return newDate;
                    },
                },
            }

            const { from: roughFrom, to: roughTo } = this.roughEventDateRange;
            const from = rangeConversion[this.calendarType].from(roughFrom);
            const to = rangeConversion[this.calendarType].to(roughTo);

            const date = new Date(from);
            for (let i = 0; date <= to && i < datesLimit; i++) {
                dates.push(new Date(date));
                if (this.calendarType === CalendarType.Date)
                    date.setDate(date.getDate() + 1);
                else if (this.calendarType === CalendarType.DateTime)
                    date.setHours(date.getHours() + 1);
            }
            return dates;
        },
        dateDisplayFunction() {
            if (this.calendarType === CalendarType.DateTime)
                return formatDateDayMonthHour;
            return formatDateDayMonth;
        },
        isPrevWeekEnabled(): boolean {
            return this.selectedWeek > 0;
        },
        isNextWeekEnabled(): boolean {
            const { from, to } = this.roughEventDateRange;
            const weeks = Math.ceil((to.getTime() - from.getTime()) / (1000 * 60 * 60 * 24 * 7));
            return this.selectedWeek < weeks - 1;
        },
    },
    methods: {
        // imported methods
        formatDateDayMonth,
        formatDateDayMonthYear,

        onDateMouseDown(date: Date) {
            this.fromDate = date;
            this.fromMode = this.isDateInSelectedDateRanges(date) ? "delete" : "add";
        },
        onDateMouseUp(date: Date) {
            if (!this.fromDate)  // this is always set, only here for typescript
                return;
            const from = this.fromDate < date ? this.fromDate : date;
            const to = this.fromDate > date ? this.fromDate : date;

            const newDateRange = {
                from: from,
                to: to,
            } as DateRange;

            if (this.fromMode === "delete") {  // date range started on a selected date
                // remove "eaten up" ranges
                this.selectedDateRanges = this.selectedDateRanges.filter(x => {
                    return !(x.from >= newDateRange.from && x.to <= newDateRange.to);
                });
                
                for (const dateRange of this.selectedDateRanges) {
                    if (dateRange.from <= newDateRange.from && newDateRange.to <= dateRange.to) {
                        // selection splits existing range
                        if (newDateRange.from > dateRange.from && newDateRange.to < dateRange.to) {
                            // add current selection to date range
                            const newDateFrom = new Date(newDateRange.from);
                            const newDateTo = new Date(newDateRange.to);
                            // add padding
                            if (this.calendarType === CalendarType.Date) {
                                newDateFrom.setDate(newDateFrom.getDate() - 1);
                                newDateTo.setDate(newDateTo.getDate() + 1);
                            } else if (this.calendarType === CalendarType.DateTime) {
                                newDateFrom.setHours(newDateFrom.getHours() - 1);
                                newDateTo.setHours(newDateTo.getHours() + 1);
                            }

                            // create new date range for last part
                            this.selectedDateRanges.push({
                                from: newDateTo,
                                to: dateRange.to,
                            });
                            // update current range for first part
                            dateRange.to = new Date(newDateFrom);
                            return;
                        }
                        // remove from start
                        if (newDateRange.from.getTime() === dateRange.from.getTime()) {
                            const newDateTo = new Date(newDateRange.to);
                            // add padding
                            if (this.calendarType === CalendarType.Date)
                                newDateTo.setDate(newDateTo.getDate() + 1);
                            else if (this.calendarType === CalendarType.DateTime)
                                newDateTo.setHours(newDateTo.getHours() + 1);

                            dateRange.from = newDateTo;
                        }
                        // remove from end
                        if (newDateRange.to.getTime() === dateRange.to.getTime()) {
                            const newDateFrom = new Date(newDateRange.from);
                            // add padding
                            if (this.calendarType === CalendarType.Date)
                                newDateFrom.setDate(newDateFrom.getDate() - 1);
                            else if (this.calendarType === CalendarType.DateTime)
                                newDateFrom.setHours(newDateFrom.getHours() - 1);

                            dateRange.to = newDateFrom;
                        }
                    }
                }
                
            } else if (this.fromMode === "add") {  // date range started on a non-selected date
                // remove "eaten up" ranges
                this.selectedDateRanges = this.selectedDateRanges.filter(x => {
                    return !(x.from >= newDateRange.from && x.to <= newDateRange.to);
                });
                // append new date range
                this.selectedDateRanges.push(newDateRange);
                // sort date ranges
                this.selectedDateRanges = this.selectedDateRanges.sort((a, b) => a.from.getTime() - b.from.getTime());
                // cleanup - join ranges
                for (const dateRange of this.selectedDateRanges) {
                    for (const siblingDateRange of this.selectedDateRanges) {
                        // skip duplicates; dateRange is always smaller than siblingDateRange
                        if (dateRange.from >= siblingDateRange.from)
                            continue;
                        // join sibling ranges
                        const nextDate = new Date(dateRange.to);
                        nextDate.setDate(nextDate.getDate() + 1);
                        if (nextDate.getTime() === siblingDateRange.from.getTime()) {
                            dateRange.to = siblingDateRange.to;
                            this.selectedDateRanges = this.selectedDateRanges.filter(x => x !== siblingDateRange);
                        }
                    }
                }
            }
            this.fromDate = null;
        },

        // dates
        isDateInSelectedDateRanges(date: Date): boolean {
            return this.selectedDateRanges
                .some(dateRange => date >= dateRange.from && date <= dateRange.to);
        },

        // weeks
        prevWeek() {
            if (this.isPrevWeekEnabled)
                this.selectedWeek--;
        },
        nextWeek() {
            if (this.isNextWeekEnabled)
                this.selectedWeek++;
        },
    },
}
</script>
