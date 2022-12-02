<template>
    <div class="calendar">
        <div
            v-for="day in days"
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
    </div>
</template>

<script lang="ts">
import { IDateRange, ICalendarDate } from '../common/interfaces';
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
        }
    },
    data() {
        return {
            days: [] as ICalendarDate[],
            touchStart: undefined as ICalendarDate|undefined,
            timeoutObj: undefined as number|undefined,
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
                new Date(d.setDate(d.getDate() + dayOfWeek)) :
                new Date(d.setDate(d.getDate() - dayOfWeek));
            
        },
        // calculate dates to display on calendar
        calculateShownDates() {
            const range = this.dateRange as IDateRange;
            const from = this.getBufferedDate(range.from, 0);
            const to = this.getBufferedDate(range.to, 0, true);

            for (let d = new Date(from); d <= to; d = new Date(d.setDate(d.getDate() + 1))) {
                this.days.push({
                    display: d.getDate(),
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
.calendar {
    $border-width: 1px;
    $border-color: black;

    box-sizing: border-box;
    flex: 1;
    display: grid;
    grid-template-columns: repeat(7, 1fr);
    border: {
        width: calc($border-width / 2);
        style: solid;
        color: $border-color;
    };

    // td
    & > div {
        display: flex;
        justify-content: center;
        align-items: center;
        border: {
            width: $border-width;
            style: solid;
            color: $border-color;
        };
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
