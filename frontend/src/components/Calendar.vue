<template>
    <div class="mx-2 mb-2">
        <!-- Controls -->
        <div
            class="flex py-2 justify-between relative"
        >
            <div class="flex gap-1 items-center">
                <custom-button
                    :click="resetSelectedDateRanges"
                    :small="true"
                    :disabled="!enableOptions"
                >
                    Reset <custom-icon class="text-sm" icon="refresh" />
                </custom-button>

                <custom-button
                    :click="invertSelectedDateRanges"
                    :small="true"
                    :disabled="!enableOptions"
                >
                    Invert <custom-icon class="text-sm" icon="invert_colors" />
                </custom-button>

                <custom-toggle
                    class="ml-3"
                    v-model="selectUnavailable"
                    :disabled="!enableOptions"
                >
                    <template v-slot:left>
                        <div
                            class="h-5 w-5 rounded-sm
                            border-2 border-main-300 bg-calendar-available"
                        ></div>
                    </template>

                    <template v-slot:right>
                        <div
                            class="h-5 w-5 rounded-sm
                            border-2 border-main-300 bg-calendar-unavailable"
                        ></div>
                    </template>
                </custom-toggle>
            </div>
            <div
                v-if="calendarType === CalendarType.DateHour"
                class="flex gap-2 items-center"
            >
                {{ unitDisplay }}: {{ selectedUnit + 1 }} / {{ numberOfAllUnits + 1 }}
                <div class="flex gap-1">
                    <custom-button
                        @click="prevUnit"
                        :small="true"
                    >
                        Prev
                    </custom-button>
                    <custom-button
                        @click="nextUnit"
                        :small="true"
                    >
                        Next
                    </custom-button>
                </div>
            </div>
        </div>

        <!-- Header -->
        <div class="flex border border-transparent">
            <div
                v-for="header in getCalendarHeader"
                class="w-full text-main-000 bg-main-500 text-center font-bold py-2"
                v-html="header"
            ></div>
        </div>

        <!-- Calendar -->
        <div :class="[{
            'grid-cols-7': calendarType === CalendarType.Date,
            'grid-flow-col grid-rows-24': calendarType === CalendarType.DateHour,
        }, 'grid']">
            <div
                v-for="calendarDate in getCalendarDates"
                class="p-[1px] h-full"
                @mousedown="onDateMouseDown(calendarDate.date)"
                @mouseup="onDateMouseUp(calendarDate.date)"
                @mouseenter="event => onDateMouseEnter(event, calendarDate.date)"
                @mouseleave="onDateMouseLeave"
                @touchstart.prevent="onDateTouchStart(calendarDate.date)"
                @touchend="onDateTouchEnd(calendarDate.date)"
            >
                <div
                    :class="[{
                        '!bg-calendar-available': isDateAvailable(calendarDate.date) && !selectUnavailable,
                        '!bg-calendar-unavailable': isDateUnavailable(calendarDate.date) || selectUnavailable && !isDateAvailable(calendarDate.date) && !isDateDisabled(calendarDate.date),
                        '!bg-calendar-disabled !cursor-not-allowed': isDateDisabled(calendarDate.date),
                    }, 'bg-calendar-default transition-colors duration-75',
                    'h-full py-2 flex items-center justify-center select-none cursor-pointer relative']"
                >
                    <!-- Heatmap overlay -->
                    <div
                        class="absolute top-0 bottom-0 left-0 right-0 bg-calendar-available"
                        :style="`opacity: ${getHeatmapValue(calendarDate)}`"
                    ></div>

                    <!-- Display value -->
                    <span class="z-10">
                        {{ dateDisplayFunction(calendarDate.date) }}
                    </span>
                </div>
            </div>
        </div>
    </div>
</template>

<script lang="ts">
import { PropType } from "vue";

import { formatDateDayMonthYear, formatDateDayMonth, formatDateHour } from "@/utils/dates";
import { CalendarType, DateRange, CalendarDate } from "@/types/calendar";

import CustomButton from "./ui/CustomButton.vue";
import CustomToggle from "./ui/CustomToggle.vue";
import CustomIcon from "./ui/CustomIcon.vue";

export default {
    name: "Calendar",
    setup() {
        return {
            CalendarType,
        }
    },
    components: {
        CustomButton,
        CustomToggle,
        CustomIcon,
    },
    emits: [ "update:selectedDateRanges" ],
    props: {
        // rough event duration for calculating pages
        roughEventDateRange: {
            type: Object as PropType<DateRange>,
            required: true,
        },
        // selected date ranges shown in green
        selectedDateRanges: {
            type: Array as PropType<DateRange[]>,
            required: true,
        },
        // selectable date ranges shown which the user can choose
        selectableDateRanges: {
            type: Array as PropType<DateRange[]>,
            default: [],
        },
        // date ranges for calculating heatmap
        heatmapDateRanges: {
            type: Array as PropType<DateRange[]>,
            default: [],
        },
        // calendar type
        calendarType: {
            type: Number as PropType<CalendarType>,
            required: true,
        },
        // should options be enabled
        enableOptions: {
            type: Boolean,
            default: true,
        },
    },
    data() {
        return {
            fromDate: null as null | Date,  // set on from date select
            fromMode: "add" as "add" | "delete",  // mode when selecting from date
            toDate: null as null | Date,  // changed on date enter

            selectUnavailable: false,  // is user selecting unavailable dates
            longpressTimeout: null as null | ReturnType<typeof setTimeout>,

            selectedUnit: 0,  // current selected unit
        }
    },
    computed: {
        // calendar
        getCalendarDates(): CalendarDate[] {
            // gets dates to display on the calendar
            if (!this.roughEventDateRange)
                return [];
            const calendarDates: CalendarDate[] = [];

            const calendarTypeLimits = {
                [CalendarType.Date]: 371,
                [CalendarType.DateHour]: 24 * 7,
            };
            const datesLimit = calendarTypeLimits[this.calendarType];
            
            // functions for calculating the correct padding for from and to dates
            const rangeConversion = {
                [CalendarType.Date]: {
                    from: (date: Date) => {
                        // get current day of the week (0-6)
                        const currentDayOfWeek = date.getDay();
                        // get first day of the week (Monday)
                        const newDate = new Date(date.setDate(
                            date.getDate() - (currentDayOfWeek === 0 ? 6 : currentDayOfWeek - 1)));
                        return newDate;
                    },
                    to: (date: Date) => {
                        // get current day of the week (0-6)
                        const currentDayOfWeek = date.getDay();
                        // get last day of the week (Sunday)
                        const newDate = new Date(date.setDate(
                            date.getDate() + (currentDayOfWeek === 0 ? 0 : 7 - currentDayOfWeek)));
                        return newDate;
                    },
                },
                [CalendarType.DateHour]: {
                    from: (date: Date) => {
                        // get current day of the week (0-6)
                        const currentDayOfWeek = date.getDay();
                        // get first day of the week (Monday)
                        const newDate = new Date(date.setDate(
                            date.getDate() - (currentDayOfWeek === 0 ? 6 : currentDayOfWeek - 1)));
                        newDate.setDate(newDate.getDate() + this.selectedUnit * 7);
                        newDate.setHours(0, 0);
                        return newDate;
                    },
                    to: (date: Date) => {
                        // get current day of the week (0-6)
                        const currentDayOfWeek = date.getDay();
                        // get last day of the week (Sunday)
                        const newDate = new Date(date.setDate(
                            date.getDate() + (currentDayOfWeek === 0 ? 0 : 7 - currentDayOfWeek)));
                        newDate.setDate(newDate.getDate() + this.selectedUnit * 7);
                        newDate.setHours(23, 59);
                        return newDate;
                    },
                },
            }

            const { start_date: roughFrom, end_date: roughTo } = this.roughEventDateRange;
            const from = rangeConversion[this.calendarType].from(roughFrom);
            const to = rangeConversion[this.calendarType].to(roughTo);

            const date = new Date(from);
            for (let i = 0; date <= to && i < datesLimit; i++) {
                // calculate heatmap if it's provided
                const heatmap = !this.isHeatmapProvided ? 0 :
                    this.heatmapDateRanges.reduce((acc, range) => {
                        if (this.isDateInDateRange(date, range))
                            acc++;
                        return acc;
                    }, 0)

                // create new date
                const calendarDate = {
                    date: new Date(date),
                    heatmap: heatmap,
                }
                calendarDates.push(calendarDate);
                this.addUnitsToDate(date, this.calendarType, 1)
            }
            return calendarDates;
        },
        getCalendarHeader(): string[] {
            const days = ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]
            if (this.calendarType === CalendarType.DateHour)
                return this.getCalendarDates
                    .filter((_, index) => index % 24 === 0)
                    .map((calendarDate, index) => `${days[index]}<br/>${formatDateDayMonth(calendarDate.date)}`);
            return days;
        },
        maxHeatmapValue(): number {
            // finds the maximum heatmap value
            if (!this.isHeatmapProvided)
                return 1;
            return this.getCalendarDates.reduce((max, range) => {
                if (range.heatmap > max)
                    return range.heatmap;
                return max;
            }, 1);
        },

        // units
        unitDisplay(): string {
            if (this.calendarType === CalendarType.DateHour)
                return "Week";
            return "Days";
        },
        isPrevUnitEnabled(): boolean {
            return this.selectedUnit > 0;
        },
        isNextUnitEnabled(): boolean {
            return this.selectedUnit < this.numberOfAllUnits;
        },
        numberOfAllUnits(): number {
            const { start_date, end_date } = this.roughEventDateRange;
            const allUnitsConversion = {
                [CalendarType.DateHour]: 1000 * 60 * 60 * 24 * 7,
                [CalendarType.Date]: 1,
            }

            return Math.ceil((end_date.getTime() - start_date.getTime()) / allUnitsConversion[this.calendarType]);
        },

        // dates
        dateDisplayFunction() {
            const formatFunctions = {
                [CalendarType.DateHour]: formatDateHour,
                [CalendarType.Date]: formatDateDayMonth,
            };
            return formatFunctions[this.calendarType];
        },
        creatingDateRange(): DateRange | null {
            // used when the user is interacting with the calendar
            if (!this.fromDate || !this.toDate)
                return null;
            // switch dates if necessary
            const from = this.fromDate < this.toDate ? this.fromDate : this.toDate;
            const to = this.fromDate > this.toDate ? this.fromDate : this.toDate;
            return {
                start_date: from,
                end_date: to,
            } as DateRange;
        },
        defaultDateRanges(): DateRange[] {
            // used when reseting the selection
            if (this.selectableDateRanges.length !== 0)
                return this.selectableDateRanges;

            // prepare the roughEventDateRange for processing
            const fromDate = new Date(this.roughEventDateRange.start_date);
            const toDate = new Date(this.roughEventDateRange.end_date);
            if (this.calendarType === CalendarType.DateHour) {
                fromDate.setHours(0, 0);
                toDate.setHours(23, 59);
            }
            
            return [{
                start_date: fromDate,
                end_date: toDate
            } as DateRange]
        },

        // heatmap
        isHeatmapProvided(): boolean {
            return this.heatmapDateRanges.length > 0;
        },
    },
    methods: {
        // imported methods
        formatDateDayMonth,
        formatDateDayMonthYear,

        // event handlers
        onDateMouseDown(date: Date) {
            if (!this.isDateInSelectableDateRanges(date))  // date is not selectable
                return;
            this.fromDate = date;
            this.toDate = date;
            this.fromMode = this.isDateInSelectedDateRanges(date) ? "delete" : "add";
        },
        onDateMouseUp(date: Date) {
            if (!this.fromDate)  // this should always be set
                return;
            if (!this.isDateInSelectableDateRanges(date))  // date is not selectable
                return;
            const from = this.fromDate < date ? this.fromDate : date;
            const to = this.fromDate > date ? this.fromDate : date;

            const newDateRange = {
                start_date: from,
                end_date: to,
            } as DateRange;

            let updateSelectedDateRanges = this.selectedDateRanges;

            if (this.fromMode === "delete") {  // date range started on a selected date
                updateSelectedDateRanges = this.deleteDateRangeFromDateRanges(newDateRange, updateSelectedDateRanges);
            } else if (this.fromMode === "add") {  // date range started on a non-selected date
                // remove "eaten up" ranges
                updateSelectedDateRanges = updateSelectedDateRanges.filter(x => {
                    return !(x.start_date >= newDateRange.start_date && x.end_date <= newDateRange.end_date);
                });
                // check for new gaps in selectableDateRanges
                if (this.selectableDateRanges) {
                    for (let i = 0; i < this.selectableDateRanges.length - 1; i++) {
                        const selectableDateRange = this.selectableDateRanges[i];
                        const nextSelctableDateRange = this.selectableDateRanges[i + 1];
                        // new date range from is inside a selected date range and to is outside
                        if (this.isDateInDateRange(newDateRange.start_date, selectableDateRange) && newDateRange.end_date > selectableDateRange.end_date) {
                            // insert a date range for the first selectable part
                            const previousDateRange = {
                                start_date: newDateRange.start_date,
                                end_date: selectableDateRange.end_date
                            } as DateRange
                            // modify the new date range to start on the next selectable date range
                            newDateRange.start_date = nextSelctableDateRange.start_date;
                            updateSelectedDateRanges.push(previousDateRange);
                        }
                    }
                }
                // append new date range
                updateSelectedDateRanges.push(newDateRange);
                // sort date ranges
                updateSelectedDateRanges = updateSelectedDateRanges.sort((a, b) => a.start_date.getTime() - b.start_date.getTime());
                // cleanup - join ranges
                for (const dateRange of updateSelectedDateRanges) {
                    for (const siblingDateRange of updateSelectedDateRanges) {
                        // skip duplicates; dateRange is always smaller than siblingDateRange
                        if (dateRange.start_date >= siblingDateRange.start_date)
                            continue;
                        // join sibling ranges
                        const nextDate = new Date(dateRange.end_date);
                        this.addUnitsToDate(nextDate, this.calendarType, 1);
                        if (nextDate.getTime() === siblingDateRange.start_date.getTime()) {
                            dateRange.end_date = siblingDateRange.end_date;
                            updateSelectedDateRanges = updateSelectedDateRanges.filter(x => x !== siblingDateRange);
                        }
                    }
                }
            }
            // emit the changes
            this.$emit("update:selectedDateRanges", updateSelectedDateRanges);
            this.fromDate = null;
        },
        onDateMouseEnter(event: MouseEvent, date: Date) {
            if (!this.isDateInSelectableDateRanges(date))  // date is not selectable
                return;
            if (event.buttons !== 1)
                return;
            this.toDate = date;
        },
        onDateMouseLeave() {
            this.toDate = null;
        },
        onDateTouchStart(date: Date) {
            if (this.fromDate === null) {  // start user selection
                this.longpressTimeout = setTimeout(() => {
                    window.navigator.vibrate(200);
                    this.onDateMouseDown(date);
                }, 350)
            } else {  // end user selection
                this.onDateMouseUp(date);
                this.longpressTimeout = null;
            }
        },
        onDateTouchEnd(date: Date) {
            // long press was canceled on same date
            if (this.fromDate?.getTime() === date.getTime() || this.longpressTimeout === null)
                return;
            clearInterval(this.longpressTimeout);
            this.longpressTimeout = null;
            // select the current date
            this.onDateMouseDown(date);
            this.onDateMouseUp(date);
        },

        // interaction handlers
        deleteDateRangeFromDateRanges(deleteDateRange: DateRange, dateRanges: DateRange[]): DateRange[] {
            // remove "eaten up" ranges
            dateRanges = dateRanges.filter(x => {
                return !(x.start_date >= deleteDateRange.start_date && x.end_date <= deleteDateRange.end_date);
            });
            
            for (const dateRange of dateRanges) {
                if (dateRange.start_date <= deleteDateRange.start_date && deleteDateRange.end_date <= dateRange.end_date) {
                    // selection splits existing range
                    if (deleteDateRange.start_date > dateRange.start_date && deleteDateRange.end_date < dateRange.end_date) {
                        // add current selection to date range
                        const newDateFrom = new Date(deleteDateRange.start_date);
                        const newDateTo = new Date(deleteDateRange.end_date);
                        // add padding
                        this.addUnitsToDate(newDateFrom, this.calendarType, -1);
                        this.addUnitsToDate(newDateTo, this.calendarType, 1);

                        // create new date range for last part
                        dateRanges.push({
                            start_date: newDateTo,
                            end_date: dateRange.end_date,
                        });
                        // update current range for first part
                        dateRange.end_date = new Date(newDateFrom);
                        continue;
                    }
                    // remove from start
                    if (deleteDateRange.start_date.getTime() === dateRange.start_date.getTime()) {
                        const newDateTo = new Date(deleteDateRange.end_date);
                        // add padding
                        this.addUnitsToDate(newDateTo, this.calendarType, 1)

                        dateRange.start_date = newDateTo;
                    }
                    // remove from end
                    if (deleteDateRange.end_date.getTime() === dateRange.end_date.getTime()) {
                        const newDateFrom = new Date(deleteDateRange.start_date);
                        // add padding
                        this.addUnitsToDate(newDateFrom, this.calendarType, -1)

                        dateRange.end_date = newDateFrom;
                    }
                }
            }
            return dateRanges;
        },

        // date helpers
        isDateInSelectedDateRanges(date: Date): boolean {
            return this.selectedDateRanges
                .some(dateRange => this.isDateInDateRange(date, dateRange));
        },
        isDateInDateRange(date: Date, dateRange: DateRange) {
            return date >= dateRange.start_date && date <= dateRange.end_date;
        },
        isDateInSelectableDateRanges(date: Date): boolean {
            if (this.selectableDateRanges.length === 0)
                return true;
            return this.selectableDateRanges
                .some(dateRange => this.isDateInDateRange(date, dateRange));
        },
        addUnitsToDate(date: Date, calendarType: CalendarType, units: number) {
            if (calendarType === CalendarType.Date)
                date.setDate(date.getDate() + units);
            else if (calendarType === CalendarType.DateHour)
                date.setHours(date.getHours() + units);
            return date;
        },
        deepCopyDateRange(dateRange: DateRange): DateRange {
            return {
                start_date: new Date(dateRange.start_date),
                end_date: new Date(dateRange.end_date),
            } as DateRange
        },
        invertSelectedDateRanges() {
            let updateSelectedDateRanges = this.defaultDateRanges.map(this.deepCopyDateRange);
            for (const selectedDateRange of this.selectedDateRanges)
                updateSelectedDateRanges = this.deleteDateRangeFromDateRanges(selectedDateRange, updateSelectedDateRanges);
            this.$emit('update:selectedDateRanges', updateSelectedDateRanges);
        },
        resetSelectedDateRanges() {
            // sets the selected date ranges either to full or empty
            const updateSelectedDateRanges = this.selectUnavailable ?
                this.defaultDateRanges.map(this.deepCopyDateRange) : []
            this.$emit('update:selectedDateRanges', updateSelectedDateRanges)
        },
        getDateRangeLength(dateRange: DateRange): number {
            const from = new Date(dateRange.start_date);
            const to = new Date(dateRange.end_date);
            return from.getTime() - to.getTime();
        },
        areDateRangesSameLengths(dateRange1: DateRange[], dateRange2: DateRange[]): boolean {
            return dateRange1.every((dateRange, index) => {
                return this.getDateRangeLength(dateRange) === this.getDateRangeLength(dateRange2[index]);
            })
        },

        // units
        prevUnit() {
            if (this.isPrevUnitEnabled)
                this.selectedUnit--;
        },
        nextUnit() {
            if (this.isNextUnitEnabled)
                this.selectedUnit++;
        },

        // calendar colors
        isDateAvailable(date: Date): boolean {
            if (this.isDateInSelectedDateRanges(date))
                return true;
            // check if date is currently selected
            return this.fromMode === 'add' &&
                this.creatingDateRange !== null &&
                this.isDateInDateRange(date, this.creatingDateRange)
        },
        isDateUnavailable(date: Date): boolean {
            // is date currently being deleted
            return this.fromMode === 'delete' &&
                this.creatingDateRange !== null &&
                this.isDateInDateRange(date, this.creatingDateRange)
        },
        isDateInPast(date: Date): boolean {
            const today = new Date()
            if (this.calendarType === CalendarType.Date)
                today.setHours(0, 0, 0, 0);
            return date <= today;
        },
        isDateDisabled(date: Date): boolean {
            return !this.isDateInSelectableDateRanges(date) || this.isDateInPast(date);
        },

        // heatmap
        getHeatmapValue(calendarDate: CalendarDate) {
            return calendarDate.heatmap / (this.maxHeatmapValue + 1);
        }
    },
    watch: {
        selectUnavailable() {
            // if selected date ranges are empty or completely full, reset whenever the unavailable is switched
            if (this.selectedDateRanges.length === 0 || this.areDateRangesSameLengths(this.selectedDateRanges, this.defaultDateRanges)) {
                this.resetSelectedDateRanges();
            }
        },
        enableOptions(enable: boolean) {
            // reset options when disabled
            if (!enable) {
                this.selectUnavailable = false;
            }
        },
    },
}
</script>
