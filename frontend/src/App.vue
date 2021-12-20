<template>
  <div
    class="
      flex flex-col
      gap-4
      md:gap-6 md:flex-row
      justify-center
      items-center
      h-screen
      bg-gradient-to-tl
      from-blue-300
      to-blue-100
    "
  >
    <router-view />
  </div>
</template>

<script>
export default {
  components: {},
};
</script>

<style>
</style>
