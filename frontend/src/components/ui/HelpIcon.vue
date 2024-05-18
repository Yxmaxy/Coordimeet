<template>
    <div class="flex">
        <!-- Help icon -->
        <custom-icon
            class="cursor-pointer size-inherit"
            :icon="icon"
            @click="showPopup = true"
        />
        <!-- Popup -->
        <div
            v-if="showPopup"
            class="fixed top-0 left-0 right-0 bottom-0 z-50
                bg-black/30 flex justify-center items-center"
            @click.self="showPopup = false"
        >
            <div class="bg-main-000 border-2 border-main-400 max-w-md m-4 p-2 rounded-md">
                <div class="flex justify-end">
                    <custom-icon
                        class="cursor-pointer"
                        icon="close"
                        @click="showPopup = false"
                    />
                </div>
                <div class="p-2">
                    <slot></slot>
                </div>
            </div>
        </div>
    </div>
</template>

<script lang="ts">
import CustomIcon from "@/components/ui/CustomIcon.vue";
export default {
    name: "HelpIcon",
    components: {
        CustomIcon,
    },
    props: {
        icon: {
            type: String,
            default: "help",
        },
    },
    data() {
        return {
            showPopup: false,
        }
    },    
}
</script>
