<template>
    <div v-if="event">
        <slot name="before"></slot>
        <div class="text-2xl font-bold">{{ event.Name }}</div>
        <div class="flex flex-col gap-1 mt-3">
            <div>Organizer: {{ event.Organizer?.FirstName }} {{ event.Organizer?.LastName }}</div>
            <div>Deadline: {{ formatDateDayMonthYear(new Date(event.Deadline)) }}</div>
            <div>Duration: {{ event.Length }} {{ readableCalendarUnits }}</div>
            <div v-for="value, key in event.Config">
                {{ key }}:
                {{ value }}
            </div>
        </div>
        <slot name="after"></slot>
    </div>
</template>

<script lang="ts">
import { PropType } from 'vue';

import { Event } from '@/types/event';
import { CalendarType } from '@/types/calendar';

import { formatDateDayMonthYear } from "@/utils/dates";

export default {
    name: "EventData",
    props: {
        event: {
            type: Object as PropType<Event>,
            required: true,
        }
    },
    computed: {
        readableCalendarUnits(): string {
            if (this.event.CalendarType === CalendarType.Date)
                return "days";
            return "hours";
        },
    },
    methods: {
        // imported
        formatDateDayMonthYear,
    }
}
</script>
