<template>
    <div class="w-full">
        <component
            :is="isTextArea ? 'textarea' : 'input'"
            :class="[{
                'bg-invalid-light border-invalid-dark': forceInvalidMessage || isInvalid,
            }, 'w-full pl-4 pr-4 pt-2 pb-2 rounded-xl text-ellipsis',
                'bg-main-000 border-2 border-main-300 focus:border-main-200 focus:outline-none']"
            :type="type"
            rows="3"
            :min="minValue"

            :placeholder="placeholder"
            :value="modelValue"
            @input="$emit('update:modelValue', $event.target.value)"

            @focus="checkRequired = false"
            @blur="checkRequired = true"
        ></component>

        <div
            v-if="!ignoreValidity"
            class="flex justify-end text-invalid-dark text-sm h-5">
            <template v-if="forceInvalidMessage || isInvalid">
                {{ invalidMessage }}
            </template>
        </div>
    </div>
</template>

<script lang="ts">
import { formatDateYMD, formatDateTimeYMD } from "@/utils/dates";

export default {
    name: "CustomInput",
    props: {
        modelValue: {
            type: [String, Number],
            required: true,
        },
        type: {
            type: String,
            default: "text",
        },
        placeholder: {
            type: String,
            default: "",
        },
        pattern: {
            type: String,
            default: ".+",
        },
        invalidMessage: {
            type: String,
            default: "This field is required",
        },
        forceInvalidMessage: {
            type: Boolean,
            default: false,
        },
        ignoreValidity: {
            type: Boolean,
            default: false,
        },
    },
    data() {
        return {
            checkRequired: false,
        }
    },
    computed: {
        isInvalid(): boolean {
            if (this.ignoreValidity)
                return false;
            const pattern = new RegExp(this.pattern);
            return this.checkRequired && !pattern.test(String(this.modelValue));
        },
        isTextArea(): boolean {
            return this.type === "textarea";
        },
        minValue(): string {
            if (this.type.startsWith("datetime"))
                return formatDateTimeYMD(new Date());
            if (this.type.startsWith("date"))
                return formatDateYMD(new Date())
            return "1";
        },
    },
}
</script>