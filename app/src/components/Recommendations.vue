<script setup>
const props = defineProps({ items: { type: Array, default: () => [] } })
</script>

<template>
  <div class="card">
    <div class="card-body">
      <h6 class="card-subtitle mb-2 text-muted">Recommended Fixes</h6>
      <ul class="mb-0 ps-3">
        <li v-for="r in items" :key="r">{{ r }}</li>
        <li v-if="!items || items.length===0" class="text-muted">No issues detected.</li>
      </ul>
    </div>
  </div>
  
</template>

<style scoped>
</style>


