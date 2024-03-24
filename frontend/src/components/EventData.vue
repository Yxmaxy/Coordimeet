<template>
    <div v-if="event">
        <slot name="before"></slot>
        <div class="text-2xl font-bold">{{ event.title }}</div>
        <div class="flex flex-col gap-1 mt-3">
            <div>Organiser: {{ event.organiser?.first_name }} {{ event.organiser?.last_name }}</div>
            <div>
                Deadline:
                <template v-if="event.deadline">{{ formatDateDayMonthYear(event.deadline) }}</template>
                <template v-else>Not set</template>
            </div>
            <div>
                Deadline:
                <template v-if="event.event_length">{{ event.event_length }} {{ readableCalendarUnits }}</template>
                <template v-else>Not set</template>
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
            if (this.event.event_calendar_type === CalendarType.Date)
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
