<template>
    <div>
        <div v-for="dateRange in selectedDateRanges">
            {{ formatDateDayMonthYear(dateRange.from) }} - {{ formatDateDayMonthYear(dateRange.to) }}
        </div>
        <div class="grid grid-cols-7 gap-0.5">
            <!-- A date element -->
            <div
                v-for="date in getCalendarDates"
                :class="[{
                    'bg-calendar-available': isDateInSelectedDateRanges(date),
                }, 'bg-calendar-in-range p-2 select-none cursor-pointer']"
                @mousedown="onDateMouseDown(date)"
                @mouseup="onDateMouseUp(date)"
            >
                {{ formatDateDayMonth(date) }}
            </div>
        </div>
    </div>
</template>

<script lang="ts">
import { PropType } from "vue";

import { formatDateDayMonthYear, formatDateDayMonth, formatDateHour, formatDateForBackend } from "@/utils/dates";
import { CalendarType, CalendarDate, DateRange, CalendarMode } from "@/types/calendar";

export default {
    name: "Calendar2",
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
            selectedDateRanges: [] as DateRange[],

            fromDate: null as null | Date,  // set on from date select
            fromMode: "add" as "add" | "delete"  // mode when selecting from date
        }
    },
    computed: {
        // gets dates to display on the calendar
        getCalendarDates(): Date[] {
            if (!this.roughEventDateRange)
                return [];
            const { from: roughFrom, to: roughTo } = this.roughEventDateRange;
            const dates: Date[] = [];
            const datePadding = 7;  // how many days to add to the calendar
            
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
                    from: (x: any) => x,
                    to: (x: any) => x,
                }
            }
            const from = rangeConversion[this.calendarType].from(roughFrom);
            const to = rangeConversion[this.calendarType].to(roughTo);

            const date = new Date(from);
            while (date <= to) {
                dates.push(new Date(date));
                date.setDate(date.getDate() + 1);
            }
            return dates;
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
                            newDateFrom.setDate(newDateFrom.getDate() - 1);
                            const newDateTo = new Date(newDateRange.to);
                            newDateTo.setDate(newDateTo.getDate() + 1);

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
                            newDateTo.setDate(newDateTo.getDate() + 1);
                            dateRange.from = newDateTo;
                        }
                        // remove from end
                        if (newDateRange.to.getTime() === dateRange.to.getTime()) {
                            const newDateFrom = new Date(newDateRange.from);
                            newDateFrom.setDate(newDateFrom.getDate() - 1);
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
    },
}
</script>
