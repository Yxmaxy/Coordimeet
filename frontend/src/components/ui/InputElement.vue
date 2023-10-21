<template>
    <div class="w-full">
        <div
            v-if="type === 'radio'"
            class="flex items-center cursor-pointer select-none gap-2"
            @click="$emit('update:modelValue', value)"
        >
            <div
                class="w-6 h-6 flex justify-center items-center
                    bg-white border-main-500 border-2 rounded-full">
                <div v-if="modelValue === value"
                    class="w-3 h-3 rounded-full bg-main-500"
                ></div>
            </div>
            {{ placeholder }}
        </div>
        
        <template v-else>
            <input
                :class="[{
                    'bg-invalid-light border-invalid-dark': isInvalid,
                }, 'w-full pl-4 pr-4 pt-2 pb-2 rounded-xl',
                    'border-2 border-main-300 focus:border-main-200 focus:outline-none']"
                :type="type"
                :placeholder="placeholder"
                :pattern="pattern"
                :inputmode="type"

                :value="modelValue"
                @input="$emit('update:modelValue', $event.target.value)"
        
                @focus="checkRequired = false"
                @blur="checkRequired = true"
            />
            <div class="flex justify-end text-invalid-dark text-sm h-5">
                <template v-if="isInvalid && invalidMessage">
                    {{ invalidMessage }}
                </template>
            </div>
        </template>
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
        value: {
            type: [String, Number],
            required: false,
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
        min: {
            type: [Number],
            default: 1,
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
        }
    },
}
</script>