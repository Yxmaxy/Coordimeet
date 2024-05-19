<template>
    <div class="flex flex-col mt-2">
        <router-link
            v-for="event in events"
            class="flex-1 flex justify-between bg-main-100 m-2 px-8 py-6 rounded-2xl
            cursor-pointer shadow-md transition-all hover:-translate-y-1 hover:bg-main-200"
            :to="`/event/${event.event_uuid}`"
        >
            <div class="flex gap-1">
                <b>{{ event.title }}</b>
                <template v-if="!userIsOrganiser">
                    -
                    <abbr title="Organiser">
                        {{ event.organiser?.first_name }} {{ event.organiser?.last_name }}
                    </abbr>
                    <custom-icon class="text-base" icon="engineering" />
                </template>
            </div>
            <div>
                <div
                    v-if="userIsOrganiser && event.selected_start_date && event.selected_end_date"
                    class="flex gap-2"
                >
                    <abbr title="Event deadline">
                        {{ formatDateDayMonthYear(new Date(event.deadline)) }}
                    </abbr>
                    <custom-icon class="text-base" icon="event_upcoming" />
                </div>
                <div
                    v-else-if="event.selected_start_date && event.selected_end_date"
                    class="flex gap-2 font-bold"
                >
                    <abbr title="Selected date">
                        {{ formatDateDayMonthYear(event.selected_start_date) }}
                        <template v-if="event.selected_start_date !== event.selected_end_date">
                            - {{ formatDateDayMonthYear(event.selected_end_date) }}
                        </template>
                    </abbr>
                    <custom-icon class="text-base" icon="event_available" />
                </div>
            </div>
        </router-link>
    </div>
</template>

<script lang="ts">
import { PropType } from "vue";
import { RouterLink } from "vue-router";
import { formatDateDayMonthYear } from "@/utils/dates";
import { Event } from "@/types/event";

import CustomIcon from "@/components/ui/CustomIcon.vue";

export default {
    name: "EventListComponent",
    components: {
        CustomIcon,
        RouterLink,
    },
    props: {
        events: {
            type: Array as PropType<Event[]>,
            default: [],
            required: true,
        },
        userIsOrganiser: {
            type: Boolean,
            default: false,
        }
    },
    methods: {
        formatDateDayMonthYear,
    },
}
</script>
