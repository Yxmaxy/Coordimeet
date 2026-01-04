<template>
    <div v-if="event">
        <slot name="before"></slot>
        <div class="text-2xl font-bold">{{ event.title }}</div>
        <div class="flex flex-col gap-1 mt-3">
            <div>Organiser: {{ organiserDisplay }}</div>
            <div>
                Deadline:
                <template v-if="event.deadline">{{ formatDateByCalendarType(event.deadline, event.event_calendar_type) }}</template>
                <template v-else>Not set</template>
            </div>
            <div>
                Length:
                <template v-if="event.event_length">{{ event.event_length }} {{ readableCalendarUnits }}</template>
                <template v-else>Not set</template>
            </div>
            <div v-if="event.description">
                {{ event.description }}
            </div>
        </div>
        <slot name="after"></slot>
    </div>
</template>

<script lang="ts">
import { PropType } from 'vue';

import { Event } from '@/types/event';
import { CalendarType } from '@/types/calendar';

import { formatDateByCalendarType } from "@/utils/dates";

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
        organiserDisplay(): string {
            if (this.event.is_group_organiser && this.event.invited_group?.name) {
                return this.event.invited_group.name;
            }
            if (this.event.organiser) {
                return this.event.organiser.user?.email;
            }
            return "";
        }
    },
    methods: {
        // imported
        formatDateByCalendarType,
    },
}
</script>
