<template>
    <div>
        <button @click="selectedWeek--">Prev</button>
        <button @click="selectedWeek++">Next</button>
    </div>
    <div class="calendar-component">
        <template v-for="(day, index) in days">
            <div
                v-if="(index >= selectedWeek * 24 * 7 && index < (1 + selectedWeek) * 24 * 7)"
                :class="{
                    'in-range': day.isInRange,
                    'available': day.isAvailable && !selectUnavailable,
                    'unavailable': day.isInRange && selectUnavailable && !day.isAvailable,
                }"
                @mousedown="(event) => onMouseDown(event, day)"
                @mouseenter="(event) => onMouseEnter(event, day)"
                @mouseup="onMouseUp"
                @mouseleave="(event) => onMouseLeave(event, day)"
            >
                {{day.display}}
            </div>
        </template>
    </div>
</template>

<script lang="ts">
import { formatDateHourDayMonth } from "../common/helpers";
import { IDateRange, ICalendarDate } from '../common/interfaces';

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
        // calculate dates to display on calendar
        calculateShownDates() {
            const range = this.dateRange as IDateRange;
            range.to.setHours(24);  // set to full day
            const from = this.getBufferedDate(range.from, 0);
            const to = this.getBufferedDate(range.to, 0, true);

            for (let d = new Date(from); d <= to; d = new Date(d.setHours(d.getHours() + 1))) {
                this.days.push({
                    display: formatDateHourDayMonth(d),
                    date: new Date(d),
                    isInRange: d >= range.from && d < range.to,
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
    grid-template-rows: repeat(24, 1fr);
    grid-auto-flow: column;
    gap: 2px;

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
