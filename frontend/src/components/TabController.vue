<template>
    <div class="flex flex-col">
        <!-- Header -->
        <div class="top-14 sticky z-20">
            <offline-component />
            <div class="flex w-full shadow-md">
                <!-- Mobile design -->
                <div
                    v-if="isMobile"
                    v-for="(tab, index) in tabs" :key="`mobile_header_${index}`"
                    :class="[{
                        'bg-main-300 text-main-100': activeTab !== index,
                        'bg-main-200': activeTab === index,
                    },
                    'flex-1 flex gap-2 items-center justify-center cursor-pointer select-none h-14',
                    'transition-colors border-r-2 last:border-r-0 border-main-200']"
                    @click="activeTab = index"
                    :ref="index === 0 ? 'mobile_tab' : undefined"
                >
                    <!-- Tab content -->
                    <span
                        v-if="!showOnlyIcon"
                        class="text-inherit"
                    >
                        {{ tab.name }}
                    </span>
                    <custom-icon
                        v-if="tab.icon"
                        :icon="tab.icon"
                    />
                </div>
                <!-- Desktop design -->
                <div
                    v-else
                    v-for="(tab, index) in tabs" :key="`desktop_header_${index}`"
                    :class="[{
                        'max-w-[20rem]': !isMobile && tab.narrow === 'sm',
                        'max-w-[25rem]': !isMobile && tab.narrow === 'md',
                    }, 'flex-1 flex items-center justify-between h-14 bg-main-100 shadow-md',
                       'border-r-2 last:border-r-0 border-main-200',
                       'font-bold text-xl px-4'
                    ]"
                >
                    <!-- Tab content -->
                    {{ tab.name }}
                    <custom-icon
                        v-if="tab.icon"
                        :icon="tab.icon"
                    />
                </div>
            </div>
        </div>
        <!-- Content -->
        <div class="flex flex-row">
            <div
                v-for="(tab, index) of tabs"
                :key="`tab_content_${index}`"
                :class="[{
                    'max-w-[20rem]': !isMobile && tab.narrow === 'sm',
                    'max-w-[25rem]': !isMobile && tab.narrow === 'md',
                    'hidden': isMobile && index !== activeTab,
                    'border-r-2 last:border-r-0 border-main-200': !isMobile,
                }, 'flex-1 min-h-[calc(100vh-7rem)]']"
            >
                <template v-if="!isMobile || index === activeTab">
                    <slot :name="tab.slot_name"></slot>
                </template>
            </div>
        </div>
    </div>
</template>
  
<script lang="ts">
import { PropType } from "vue";

import { Tab } from "@/types/tabs";
import { useStoreOnline } from "@/stores/storeOnline";

import OfflineComponent from "@/components/OfflineComponent.vue";
import CustomIcon from "@/components/ui/CustomIcon.vue";

export default {
    name: "TabController",
    components: {
        OfflineComponent,
        CustomIcon,
    },
    props: {
        tabs: {
            type: Array as PropType<Tab[]>,
            required: true,
        },
        breakpoint: {
            type: Number,
            default: 850,
        },
    },
    setup() {
        const storeOnline = useStoreOnline();
        return {
            storeOnline,
        }
    },
    data() {
        return {
            isMobile: true,
            showOnlyIcon: false,
            activeTab: 0,
        }
    },
    computed: {
        doAllTabsHaveIcons(): boolean {
            return this.tabs.every(tab => tab.icon);
        },
    },
    methods: {
        checkScreenSize() {
            this.isMobile = window.innerWidth <= this.breakpoint;
            if (this.$refs.mobile_tab) {
                const mobileTab = (this.$refs.mobile_tab as HTMLDivElement[])[0];
                if (mobileTab) {
                    this.showOnlyIcon = mobileTab.offsetWidth < 220 && this.doAllTabsHaveIcons;
                }
            }
        },
    },
    mounted() {
        window.addEventListener('resize', this.checkScreenSize);
        this.$nextTick(() => {
            this.checkScreenSize();
        });
    },
    unmounted() {
        window.removeEventListener('resize', this.checkScreenSize);
    },
}
</script>
