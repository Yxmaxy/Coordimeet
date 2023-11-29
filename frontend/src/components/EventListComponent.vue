<template>
    <div class="flex flex-col mt-2">
        <div
            v-for="event in events"
            class="flex-1 flex justify-between bg-main-100 m-2 px-8 py-6 rounded-2xl
            cursor-pointer shadow-md transition-all hover:-translate-y-1 hover:bg-main-200"
            @click="$router.push(`/event/${event.IDEvent}`)"
        >
            <div>
                <b>{{ event.Name }}</b>
                <template v-if="!userIsOrganiser">
                    -
                    <abbr title="Organizer">
                        {{ event.Organizer?.FirstName }} {{ event.Organizer?.LastName }}
                    </abbr>
                </template>
            </div>
            <div>
                <abbr
                    v-if="userIsOrganiser && event.SelectedDate === null"
                    title="Event deadline"
                >
                    {{ formatDateDayMonthYear(new Date(event.Deadline)) }}
                </abbr>
                <abbr
                    v-else
                    title="Selected date"
                    class="font-bold"
                >
                    {{ event.SelectedDate }}
                </abbr>
            </div>
        </div>
    </div>
</template>

<script lang="ts">
import { PropType } from "vue";
import { formatDateDayMonthYear } from "@/utils/dates";
import { Event } from "@/types/event";

export default {
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
