<template>
    <div class="flex flex-col">
        <!-- Header -->
        <div class="flex z-20 sticky top-14 w-full shadow-md">
            <!-- Tab design -->
            <div
                v-if="isMobile"
                v-for="(slotName, index) of Object.keys($slots)" :key="index"
                :class="[{
                    'bg-main-300 text-main-100': activeTab !== index,
                    'bg-main-200 text-main-700': activeTab === index,
                },
                'flex-1 flex items-center justify-center cursor-pointer select-none h-14',
                'transition-colors border-r-2 last:border-r-0 border-main-200']"
                @click="$emit('update:activeTab', index)"
            >
                {{ tabName[slotName] }}
            </div>
            <!-- Normal design -->
            <div
                v-else
                v-for="(slotName, index) of Object.keys($slots)" :key="`${index}_else`"
                :class="[{
                    'first:max-w-[25rem]': !isMobile && firstNarrow,
                }, 'flex-1 flex items-center h-14 bg-main-100 shadow-md',
                   'border-r-2 last:border-r-0 border-main-200',
                   'font-bold text-xl px-4'
                ]"
            >
                {{ tabName[slotName] }}
            </div>
        </div>
        <!-- Content -->
        <div class="flex flex-row">
            <div
                v-for="(slot, index) of Object.keys($slots)"
                :key="index"
                :class="[{
                    'first:max-w-[25rem]': !isMobile && firstNarrow,
                    'hidden': isMobile && index !== activeTab,
                    'border-r-2 last:border-r-0 border-main-200': !isMobile,
                }, 'flex-1 min-h-[calc(100vh-7rem)]']"
            >
                <div v-if="!isMobile || index === activeTab">
                    <slot :name="slot"></slot>
                </div>
            </div>
        </div>
    </div>
</template>
  
<script lang="ts">
import { tabName } from '@/utils/tabs';

export default {
    name: "TabController",
    setup() {
        return {
            tabName: tabName as any,
        }
    },
    props: {
        activeTab: {
            type: Number,
            default: 0,
        },
        firstNarrow: {
            type: Boolean,
            default: false,
        }
    },
    data() {
        return {
            isMobile: false,
        }
    },
    methods: {
        checkIsMobile() {
            this.isMobile = window.innerWidth <= 768;
        },
    },
    mounted() {
        window.addEventListener('resize', this.checkIsMobile);
        this.checkIsMobile();
    },
    unmounted() {
        window.removeEventListener('resize', this.checkIsMobile);
    },
}
</script>
