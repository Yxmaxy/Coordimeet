<template>
    <div class="flex flex-col mt-2">
        <div
            v-for="event in events"
            class="flex-1 flex justify-between bg-main-100 m-2 px-8 py-6 rounded-2xl
            cursor-pointer shadow-md transition-all hover:-translate-y-1 hover:bg-main-200"
            @click="$router.push(`/event/${event.IDEvent}`)"
        >
            <div class="flex gap-1">
                <b>{{ event.Name }}</b>
                <template v-if="!userIsOrganiser">
                    -
                    <abbr title="Organizer">
                        {{ event.Organizer?.first_name }} {{ event.Organizer?.last_name }}
                    </abbr>
                    <custom-icon class="text-base" icon="engineering" />
                </template>
            </div>
            <div>
                <div
                    v-if="userIsOrganiser && event.SelectedDate === null"
                    class="flex gap-2"
                >
                    <abbr title="Event deadline">
                        {{ formatDateDayMonthYear(new Date(event.Deadline)) }}
                    </abbr>
                    <custom-icon class="text-base" icon="event_upcoming" />
                </div>
                <div
                    v-else-if="event.SelectedDate !== null"
                    class="flex gap-2 font-bold"
                >
                    <abbr title="Selected date">
                        {{ event.SelectedDate }}
                    </abbr>
                    <custom-icon class="text-base" icon="event_available" />
                </div>
            </div>
        </div>
    </div>
</template>

<script lang="ts">
import { PropType } from "vue";
import { formatDateDayMonthYear } from "@/utils/dates";
import { Event } from "@/types/event";

import CustomIcon from "@/components/ui/CustomIcon.vue";

export default {
    name: "EventListComponent",
    components: {
        CustomIcon,
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
