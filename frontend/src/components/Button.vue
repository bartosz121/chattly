<template>
    <button @click="onClick()" :class="className" :type="this.type">
        <slot />
    </button>
</template>

<script>
export default {
    name: "Button",
    props: {
        type: {
            type: String,
            default: 'button'
        },
        bg: {
            type: String,
            default: "bg-sky-500 hover:bg-sky-600"
        },
        textColor: {
            type: String,
            default: "text-white"
        },
        sizing: {
            type: String,
            default: "py-2 px-4 rounded"
        },
        extendStyle: {
            type: String,
            default: ''
        }
    },
    methods: {
        onClick(){
            this.$emit('btn-click')
        }
    },
    computed: {
        className() {
            return `${this.bg} ${this.textColor} ${this.sizing} ${this.extendStyle}`
        },
    }
}
</script>