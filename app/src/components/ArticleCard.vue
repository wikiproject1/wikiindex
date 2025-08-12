<script setup>
import TrustScoreBar from './TrustScoreBar.vue'

const props = defineProps({
  loading: { type: Boolean, default: false },
  title: { type: String, default: '' },
  summary: { type: String, default: '' },
  url: { type: String, default: '' },
  score: { type: Number, default: 0 }
})
</script>

<template>
  <div class="card shadow-sm">
    <div class="card-body">
      <template v-if="loading">
        <div class="placeholder-glow">
          <h4 class="card-title"><span class="placeholder col-7"></span></h4>
          <p class="card-text"><span class="placeholder col-12"></span></p>
          <p class="card-text"><span class="placeholder col-10"></span></p>
          <p class="card-text"><span class="placeholder col-8"></span></p>
          <div class="mt-3"><span class="placeholder col-6"></span></div>
        </div>
      </template>
      <template v-else>
        <h3 class="card-title mb-2">{{ title }}</h3>
        <p class="card-text text-secondary">{{ summary }}</p>
        <div class="my-3">
          <TrustScoreBar :score="score" />
        </div>
        <a v-if="url" class="btn btn-outline-primary" :href="url" target="_blank" rel="noopener">
          <i class="bi bi-box-arrow-up-right me-1"></i>
          Read on Wikipedia
        </a>
      </template>
    </div>
  </div>
</template>

 

<style scoped>
</style>


