<template>
    <div class="w-full relative">
        <div
            v-if="isOpen"
            class="fixed top-0 right-0 left-0 bottom-0"
            @click="isOpen = false"
        ></div>

        <label :class="[{
            'rounded-t-xl': isOpen,
            'rounded-xl': !isOpen,
        }, 'flex justify-between items-center overflow-clip',
            'bg-white border-2 border-main-300 bg-main-000'
        ]">
            <input
                v-model="search"
                type="text"
                :placeholder="placeholderData"
                :class="[{
                    'placeholder-black': modelValue,
                    'cursor-pointer': !isOpen,
                }, 'flex-1 pl-4 pr-4 pt-2 pb-2 focus:outline-none']"
                @focus="isOpen = true"
                @keydown.enter="onConfirmedOption(search)"
            >
            <custom-icon :icon="dropdownIcon" class="pr-4" />
        </label>
        <div
            v-if="isOpen"
            class="absolute top-10 right-0 left-0 overflow-hidden z-10
            bg-white border-2 border-t-0 rounded-b-xl border-main-300 bg-main-000"
        >
            <div class="flex flex-col overflow-auto max-h-40">
                <div
                    v-for="option in filteredOptions"
                    :key="option.value"
                    class="px-4 py-2 cursor-pointer hover:bg-main-100"
                    @click="selectOption(option)"
                >
                    {{ option.text }}
                </div>
                <div
                    v-if="filteredOptions.length === 0"
                    class="px-4 py-2 cursor-pointer"
                >
                    No results
                </div>
            </div>
        </div>
    </div>
</template>

<script lang="ts">
import { PropType } from "vue";
import { SelectOption } from "@/types/ui";

import CustomIcon from "@/components/ui/CustomIcon.vue";

export default {
    name: "CustomSelect",
    emits: ["update:modelValue", "confirmedOption"],
    components: {
        CustomIcon,
    },
    props: {
        modelValue: {
            type: [String, Number],
            default: "",
        },
        placeholder: {
            type: String,
            default: "",
        },
        options: {
            type: Array as PropType<SelectOption<any>[]>,
            required: true,
        },
    },
    data() {
        return {
            search: "",
            isOpen: false,
            placeholderData: this.placeholder,
        };
    },
    computed: {
        filteredOptions() {
            return this.options.filter((option) =>
                option.text.toLowerCase().includes(this.search.toLowerCase())
            );
        },
        dropdownIcon() {
            return this.isOpen ? "arrow_drop_up" : "arrow_drop_down";
        },
    },
    methods: {
        selectOption(option: SelectOption<any>) {
            this.$emit("update:modelValue", option.value);
            this.onConfirmedOption(option.value);

            this.placeholderData = option.text;
            this.isOpen = false;
            this.search = "";

        },
        onConfirmedOption(value: number | string) {
            const option = this.options.find(option => option.value === value);
            if (option) {
                this.$emit("confirmedOption", option);
            }
        },
    },
    mounted() {
        if (this.modelValue) {
            const option = this.options.find(
                (option) => option.value === this.modelValue
            );
            if (option) {
                this.placeholderData = option.text;
            }
        }
    },
}
</script>
