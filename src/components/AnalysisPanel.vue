<script setup>
const props = defineProps({
  aiRisk: { type: Number, default: 0 },
  brokenLinks: { type: Number, default: 0 },
  brokenExternalLinks: { type: Array, default: () => [] },
  contentType: { type: String, default: 'article' },
  linksInternal: { type: Number, default: 0 },
  linksExternal: { type: Number, default: 0 },
  categories: { type: Array, default: () => [] },
  isLiving: { type: Boolean, default: false },
  isDead: { type: Boolean, default: false },
  birthYear: { type: Number, default: null },
  deathYear: { type: Number, default: null },
  isStub: { type: Boolean, default: false },
  aiExplanation: { type: String, default: '' },
  loading: { type: Boolean, default: false }
})

const riskLabel = (r) => {
  if (r >= 0.7) return 'High'
  if (r >= 0.4) return 'Medium'
  return 'Low'
}
</script>

<template>
  <div v-if="loading" class="text-center py-5">
    <div class="spinner-border text-primary" role="status">
      <span class="visually-hidden">Loading...</span>
    </div>
    <p class="mt-3 text-muted">Analyzing article...</p>
  </div>
  
  <div v-else class="row g-3">
    <div class="col-md-4">
      <div class="card h-100">
        <div class="card-body">
          <h6 class="card-subtitle mb-2 text-muted">AI Content Risk</h6>
          <div class="d-flex align-items-baseline gap-2">
            <span class="display-6">{{ Math.round(aiRisk * 100) }}%</span>
            <span class="badge" :class="{
              'bg-danger': aiRisk >= 0.7,
              'bg-warning text-dark': aiRisk >= 0.4 && aiRisk < 0.7,
              'bg-success': aiRisk < 0.4
            }">{{ riskLabel(aiRisk) }}</span>
          </div>
          <small class="text-muted">Heuristic estimate from summary text.</small>
        </div>
      </div>
    </div>

    <div class="col-md-4">
      <div class="card h-100">
        <div class="card-body">
          <h6 class="card-subtitle mb-2 text-muted">Broken Links</h6>
          <div class="display-6">{{ brokenLinks }}</div>
          <ul class="mt-2 mb-0 ps-3">
            <li v-for="u in brokenExternalLinks" :key="u">
              <a :href="u" target="_blank" rel="noopener">{{ u }}</a>
            </li>
            <li v-if="!brokenExternalLinks || brokenExternalLinks.length===0" class="text-muted">(sample of external links checked)</li>
          </ul>
        </div>
      </div>
    </div>

    <div class="col-md-4">
      <div class="card h-100">
        <div class="card-body">
          <h6 class="card-subtitle mb-2 text-muted">Content Type</h6>
          <div class="display-6 text-capitalize">{{ contentType }}</div>
        </div>
      </div>
    </div>

    <div class="col-md-6">
      <div class="card h-100">
        <div class="card-body">
          <h6 class="card-subtitle mb-2 text-muted">Links</h6>
          <div class="d-flex gap-4">
            <div>
              <div class="fw-semibold">Internal</div>
              <div class="display-6">{{ linksInternal }}</div>
            </div>
            <div>
              <div class="fw-semibold">External</div>
              <div class="display-6">{{ linksExternal }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="col-md-6">
      <div class="card h-100">
        <div class="card-body">
          <h6 class="card-subtitle mb-2 text-muted">Categories</h6>
          <div v-if="categories && categories.length > 0" class="mb-2">
            <div v-for="c in categories" :key="c" class="badge bg-light text-dark me-1 mb-1">{{ c }}</div>
          </div>
          <div v-else class="text-muted mb-2">No categories found</div>
          <div class="d-flex flex-wrap gap-2">
            <span class="badge" :class="isStub ? 'bg-warning text-dark' : 'bg-secondary'">Stub: {{ isStub ? 'Yes' : 'No' }}</span>
            <span class="badge" :class="isLiving ? 'bg-success' : 'bg-secondary'">Living: {{ isLiving ? 'Yes' : 'No' }}</span>
            <span v-if="birthYear" class="badge bg-success text-white">Born: {{ birthYear }}</span>
            <span v-else class="badge bg-secondary">Born: —</span>
            <span v-if="isDead && deathYear" class="badge bg-danger text-white">Died: {{ deathYear }}</span>
            <span v-else-if="isDead" class="badge bg-danger text-white">Deceased</span>
            <span v-else-if="!isLiving" class="badge bg-secondary">Status: Unknown</span>
          </div>
        </div>
      </div>
    </div>

    <div class="col-12">
      <div class="card border-primary">
        <div class="card-header bg-primary text-white">
          <h6 class="card-subtitle mb-0"><i class="bi bi-robot me-2"></i>AI Analysis</h6>
        </div>
        <div class="card-body">
          <p class="mb-0">{{ aiExplanation || 'No AI analysis available.' }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
</style>


