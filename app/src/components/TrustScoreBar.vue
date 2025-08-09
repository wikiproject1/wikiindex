<script setup>
import { computed } from 'vue'

const props = defineProps({
  score: { type: Number, default: 0 }
})

const clamped = computed(() => Math.max(0, Math.min(100, Math.round(props.score || 0))))

const barClass = computed(() => {
  if (clamped.value <= 40) return 'bg-danger'
  if (clamped.value <= 70) return 'bg-warning'
  return 'bg-success'
})
</script>

<template>
  <div>
    <div class="d-flex justify-content-between align-items-center mb-1">
      <small class="text-muted">Trust Score</small>
      <small class="fw-semibold">{{ clamped }}%</small>
    </div>
    <div class="progress" role="progressbar" aria-label="Trust Score" :aria-valuenow="clamped" aria-valuemin="0" aria-valuemax="100">
      <div class="progress-bar" :class="barClass" :style="{ width: clamped + '%' }"></div>
    </div>
  </div>
  
</template>

<style scoped>
</style>


