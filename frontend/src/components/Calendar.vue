<template>
    <div v-if="(type === 1)">
        <button @click="selectedWeek--">Prev</button>
        <button @click="selectedWeek++">Next</button>
    </div>
    <div :class="{'calendar-component': true, 'type-datetime': type === 1}">
        <template v-for="(day, index) in days">
            <div
                v-if="type === 0 || (index >= selectedWeek * 24 * 7 && index < (1 + selectedWeek) * 24 * 7)"
                :class="{
                    'in-range': day.isInRange,
                    'available': day.isAvailable && !selectUnavailable,
                    'unavailable': day.isInRange && selectUnavailable && !day.isAvailable,
                }"
                @mousedown="(event) => onMouseDown(event, day)"
                @mouseenter="(event) => onMouseEnter(event, day)"
                @mouseup="onMouseUp"
                @mouseleave="(event) => onMouseLeave(event, day)"
                @touchstart="(event) => onTouchStart(event, day)"
                @touchend="(event) => onTouchEnd(event, day)"
            >
                {{day.display}}
            </div>
        </template>
    </div>
</template>

<script lang="ts">
import { formatDateDayMonth, formatDateHourDayMonth } from "../common/helpers";
import { IDateRange, ICalendarDate, CalendarType } from '../common/interfaces';
const longpressTimeout = 475;

export default {
    name: "calendar",
    props: {
        dateRange: {
            type: Object,
            default: {
                from: new Date(),
                to: new Date()
            } as IDateRange
        },
        selectUnavailable: {
            type: Boolean,
            default: false
        },
        type: {
            type: Number,
            default: CalendarType.Date
        },
    },
    data() {
        return {
            days: [] as ICalendarDate[],
            touchStart: undefined as ICalendarDate|undefined,
            timeoutObj: undefined as number|undefined,
            selectedWeek: 0,
        }
    },
    methods: {
        // converts sun-mon to mon-sun
        // mon = 0; sun = 6
        getDayMonToSun(date: Date): number {
            const res = date.getDay() - 1;
            return res < 0 ? 6 : res;
        },
        // method gets date and returns start/end of the week the date is in
        getBufferedDate(date: Date, buffer: number = 0, end: boolean = false): Date {
            const d = new Date(date);  // copy date
            const dayOfWeek = (end ? 6 - this.getDayMonToSun(d) : this.getDayMonToSun(d)) + buffer;
            return end ?
                new Date(new Date(d.setDate(d.getDate() + dayOfWeek)).setHours(23)) :
                new Date(d.setDate(d.getDate() - dayOfWeek));
        },
        // increment date by hour or day
        incrementDate(date: Date): Date {
            if (this.type === CalendarType.Date)
                return new Date(date.setDate(date.getDate() + 1));
            return new Date(date.setHours(date.getHours() + 1));
        },
        // calculate dates to display on calendar
        calculateShownDates() {
            const range = this.dateRange as IDateRange;
            if (this.type === CalendarType.DateTime)
                range.to.setHours(24);  // set to full day
            const from = this.getBufferedDate(range.from, 0);
            const to = this.getBufferedDate(range.to, 0, true);

            for (let d = new Date(from); d <= to; d = this.incrementDate(d)) {
                this.days.push({
                    display: (this.type === CalendarType.Date) ?
                        formatDateDayMonth(d) : formatDateHourDayMonth(d),
                    date: new Date(d),
                    isInRange: d >= range.from && d <= range.to,
                });
            }
        },
        selectDateFromTo(start: ICalendarDate, end: ICalendarDate, setAvailable: boolean = true) {
            const from = start.date < end.date ? start : end;
            const to = start.date < end.date ? end : start;
            for (const day of this.days) {
                if (day.date >= from.date && day.date <= to.date && day.isInRange)
                    day.isAvailable = setAvailable;
            }
        },
        // methods for selecting available
        onMouseDown(event: MouseEvent, day: ICalendarDate) {
            if (!day.isInRange)
                return;
            this.touchStart = day;
            day.isAvailable = !day.isAvailable;
        },
        onMouseEnter(event: MouseEvent, day: ICalendarDate) {
            if (event.buttons === 1 && this.touchStart !== undefined) {
                this.selectDateFromTo(this.touchStart, day, !this.touchStart.isAvailable);
            }
        },
        onMouseUp() {
            this.touchStart = undefined;
        },
        onMouseLeave(event: MouseEvent, day: ICalendarDate) {
            if (event.buttons === 1 && this.touchStart !== undefined) {
                this.selectDateFromTo(this.touchStart, day, !this.touchStart.isAvailable);
            }
        },
        // methods for mobile devices
        onTouchStart(event: TouchEvent, day: ICalendarDate) {
            event.preventDefault();
            if (this.touchStart === undefined) {  // press on first date
                this.timeoutObj = setTimeout(() => {  // if event is longpress select multiple
                    // Longpress event
                    window.navigator.vibrate(200);
                    this.touchStart = day;
                    this.timeoutObj = undefined;
                }, longpressTimeout);
            } else {  // press on first date if previous press was longpress
                this.selectDateFromTo(this.touchStart, day, !this.touchStart.isAvailable);
                this.touchStart = undefined;
            }
        },
        onTouchEnd(event: TouchEvent, day: ICalendarDate) {
            if (this.timeoutObj !== undefined) {
                // Normal event
                day.isAvailable = !day.isAvailable;
            }
            clearInterval(this.timeoutObj);
            this.timeoutObj = undefined;
        },
    },
    mounted() {
        this.calculateShownDates();
    },
};
</script>
<style lang="scss" scoped>
.calendar-component {
    box-sizing: border-box;
    flex: 1;
    display: grid;
    grid-template-columns: repeat(7, 1fr);
    gap: 2px;

    &.type-datetime {
        grid-template-rows: repeat(24, 1fr);
        grid-auto-flow: column;
        grid-template-columns: unset !important;
    }

    // td
    & > div {
        display: flex;
        justify-content: center;
        align-items: center;
        box-sizing: border-box;
        cursor: pointer;
        user-select: none;
    }
    .in-range {
        background-color: lightgoldenrodyellow;
    }
    .available {
        background-color: lightgreen;
    }
    .unavailable {
        background-color: lightcoral;
    }
}
</style>
