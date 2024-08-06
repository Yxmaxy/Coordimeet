<template>
    <div class="flex flex-col mt-2 pb-20">
        <div
            v-for="event in events"
            class="flex-1 flex justify-between bg-main-100 m-2 px-8 py-6 rounded-2xl
            cursor-pointer shadow-md transition-all hover:-translate-y-1 hover:bg-main-200"
            @click="() => $router.push(`/event/${event.event_uuid}`)"
        >
            <div class="flex justify-between w-full">
                <div>
                    <b>{{ event.title }}</b>
                    <div class="flex align-middle gap-1 text-sm">
                        <abbr
                            v-if="event.is_group_organiser"
                            class="no-underline"
                            title="Organiser group"
                        >
                            <custom-icon class="text-sm" icon="group" />
                            {{ event.invited_group?.name }}
                        </abbr>
                        <abbr
                            v-else
                            class="no-underline"
                            title="Organiser"
                        >
                            <custom-icon class="text-sm" icon="person" />
                            {{ event.organiser?.email }}
                        </abbr>
                    </div>
                </div>
                <div class="flex gap-2 items-center">
                    <template v-if="!event.selected_start_date && !event.selected_end_date">
                        <custom-button
                            class="h-8 w-8 rounded-full !text-base"
                            @click.stop="() => $router.push(`/event/${event.event_uuid}`)"
                        >
                            <custom-icon v-if="event.user_response === null" icon="calendar_today" title="Respond to event" />
                            <custom-icon v-if="event.user_response === false" icon="event_busy" title="Not comming" />
                            <custom-icon v-if="event.user_response === true" icon="event_available" title="Comming to event" />
                        </custom-button>
                        <custom-button
                            v-if="userIsOrganiser && storeOnline.isOnline"
                            class="h-8 w-8 rounded-full !text-base"
                            @click.stop="() => $router.push(`/event/edit/${event.event_uuid}`)"
                        >
                            <custom-icon icon="edit" />
                        </custom-button>
                    </template>
                    <div v-else-if="userIsOrganiser" class="flex gap-3 items-center">
                        <abbr class="no-underline" title="Selected date">
                            {{
                                formatDateRange({
                                    start_date: event.selected_start_date!,
                                    end_date: event.selected_end_date!
                                }, event.event_calendar_type, false)
                            }}
                        </abbr>
                        <custom-button class="h-8 w-8 rounded-full !text-base">
                            <custom-icon icon="event_repeat" @click.stop="() => $router.push({name: 'event_new', params: { uuid: event.event_uuid }})"/>
                        </custom-button>
                    </div>
                    
                </div>
            </div>
        </div>
    </div>
</template>

<script lang="ts">
import { PropType } from "vue";
import { formatDateRange } from "@/utils/dates";
import { Event } from "@/types/event";

import { useStoreOnline } from "@/stores/storeOnline";

import CustomIcon from "@/components/ui/CustomIcon.vue";
import CustomButton from "@/components/ui/CustomButton.vue";

export default {
    name: "EventListComponent",
    components: {
        CustomIcon,
        CustomButton,
    },
    setup() {
        const storeOnline = useStoreOnline();
        return {
            storeOnline,
        }
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
        formatDateRange,
    },
}
</script>
