<template>
  <div class="flex items-center" @click="onClick">
    <h2 class="select-none pr-2">{{isActive ? trueMsg : falseMsg}}</h2>
    <div class="w-12 h-5 flex items-center bg-gray-300 rounded-full p-1 duration-300 ease-in-out" :class="{ 'bg-blue-700': isActive}">
      <div class="bg-white w-4 h-4 rounded-full shadow-md transform duration-300 ease-in-out" :class="{ 'translate-x-6': isActive,}"></div>
    </div>
  </div>
</template>

<script>
export default {
    name: "ToggleSwitch",
    props: {
        trueMsg: String,
        falseMsg: String,
        initBool: {
            default: false,
            type: Boolean
        }
    },
    data(){
        return {
            isActive: false,
        }
    },
    created(){
        this.isActive = this.initBool;
    },
    methods: {
        onClick(){
            this.isActive = !this.isActive
            this.$emit("toggle-switch", this.isActive)
        }
    }
}
</script>

<style>

</style>