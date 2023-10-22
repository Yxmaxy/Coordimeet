<template>
    <div class="w-full">
        <component
            :is="isTextArea ? 'textarea' : 'input'"
            :class="[{
                'bg-invalid-light border-invalid-dark': isInvalid,
            }, 'w-full pl-4 pr-4 pt-2 pb-2 rounded-xl',
                'border-2 border-main-300 focus:border-main-200 focus:outline-none']"
            :type="type"
            rows="3"
            min="1"

            :placeholder="placeholder"
            :value="modelValue"
            @input="$emit('update:modelValue', $event.target.value)"

            @focus="checkRequired = false"
            @blur="checkRequired = true"
        ></component>
        <div class="flex justify-end text-invalid-dark text-sm h-5">
            <template v-if="isInvalid && invalidMessage">
                {{ invalidMessage }}
            </template>
        </div>
    </div>
</template>

<script lang="ts">

export default {
    name: "InputElement",
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
    },
    data() {
        return {
            checkRequired: false,
        }
    },
    computed: {
        isInvalid(): boolean {
            const pattern = new RegExp(this.pattern);
            return this.checkRequired && !pattern.test(this.modelValue);
        },
        isTextArea(): string {
            return this.type === "textarea";
        }
    },
}
</script>