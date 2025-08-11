<script setup>
const props = defineProps({
  title: { type: String, required: true },
  items: { type: Array, default: () => [] },
  type: { type: String, default: 'internal' } // 'internal' | 'external'
})

const makeHref = (item) => {
  if (props.type === 'external') return item
  // internal
  const encoded = encodeURIComponent(item)
  return `https://sw.wikipedia.org/wiki/${encoded}`
}
</script>

<template>
  <div class="card h-100">
    <div class="card-body">
      <h6 class="card-subtitle mb-2 text-muted">{{ title }}</h6>
      <ul class="list-unstyled mb-0 links-list">
        <li v-for="it in items" :key="it">
          <a :href="makeHref(it)" target="_blank" rel="noopener" class="text-decoration-none">
            <i v-if="type==='external'" class="bi bi-box-arrow-up-right me-1"></i>
            <i v-else class="bi bi-link-45deg me-1"></i>
            {{ it }}
          </a>
        </li>
        <li v-if="!items || items.length===0" class="text-muted">—</li>
      </ul>
    </div>
  </div>
</template>

<style scoped>
.links-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: .5rem 1rem;
}
</style>


