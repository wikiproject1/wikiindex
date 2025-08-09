<script setup>
import { ref } from 'vue'
import axios from 'axios'
import SearchBar from './components/SearchBar.vue'
import ArticleCard from './components/ArticleCard.vue'
import AnalysisPanel from './components/AnalysisPanel.vue'
import LinksList from './components/LinksList.vue'

const loading = ref(false)
const article = ref({ title: '', summary: '', url: '' })
const score = ref(0)
const analysis = ref({
  ai_content_risk: 0,
  broken_links_count: 0,
  content_type: 'article',
  total_links_internal: 0,
  total_links_external: 0,
  internal_links: [],
  external_links: [],
  categories: [],
  is_living: false,
  is_dead: false,
  birth_year: null,
  is_stub: false,
})

async function fetchWikipedia(title) {
  try {
    loading.value = true
    article.value = { title: '', summary: '', url: '' }
    score.value = 0
    analysis.value = {
      ai_content_risk: 0,
      broken_links_count: 0,
      content_type: 'article',
      total_links_internal: 0,
      total_links_external: 0,
      categories: [],
      is_living: false,
      is_dead: false,
      birth_year: null,
      is_stub: false,
    }

    const summaryRes = await axios.get(
      `https://sw.wikipedia.org/api/rest_v1/page/summary/${encodeURIComponent(title)}`
    )
    const data = summaryRes.data
    article.value.title = data.title || title
    article.value.summary = data.extract || ''
    article.value.url = data.content_urls?.desktop?.page || data.content_urls?.mobile?.page || ''

    // Placeholder trust score (deterministic from title)
    score.value = Math.min(100, Math.max(0, (hashString(title) % 100)))

    // Call backend analysis
    try {
      const resp = await axios.post('http://127.0.0.1:8000/analyze', { title })
      analysis.value = resp.data
    } catch (e) {
      console.warn('Analysis backend not available yet')
    }
  } catch (err) {
    console.error(err)
    article.value = { title: 'Haijapatikana', summary: 'Imeshindwa kupata makala.', url: '' }
    score.value = 0
  } finally {
    loading.value = false
  }
}

function hashString(str) {
  let h = 0
  for (let i = 0; i < str.length; i++) {
    h = (h * 31 + str.charCodeAt(i)) >>> 0
  }
  return h
}
</script>

<template>
  <div class="min-vh-100" style="background: linear-gradient(180deg, #f8f9fa 0%, #ffffff 100%);">
    <nav class="navbar navbar-light bg-white border-bottom sticky-top">
      <div class="container">
        <span class="navbar-brand mb-0 h1 d-flex align-items-center">
          <i class="bi bi-shield-check text-primary me-2"></i>
          WikiTrust Index
        </span>
      </div>
    </nav>

    <section class="container py-5 d-flex flex-column align-items-center">
      <SearchBar @analyze="fetchWikipedia" />
    </section>

    <section class="container pb-5" style="max-width: 900px;">
      <ArticleCard :loading="loading" :title="article.title" :summary="article.summary" :url="article.url" :score="score" />
    </section>

    <section v-if="article.title" class="container pb-5" style="max-width: 1100px;">
      <AnalysisPanel
        :ai-risk="analysis.ai_content_risk"
        :broken-links="analysis.broken_links_count"
        :broken-external-links="analysis.broken_external_links"
        :content-type="analysis.content_type"
        :links-internal="analysis.total_links_internal"
        :links-external="analysis.total_links_external"
        :categories="analysis.categories"
        :is-living="analysis.is_living"
        :is-dead="analysis.is_dead"
        :death-year="analysis.death_year"
        :birth-year="analysis.birth_year"
        :is-stub="analysis.is_stub"
        :ai-explanation="analysis.ai_explanation"
      />

      <div class="row g-3 mt-0" v-if="analysis.internal_links?.length || analysis.external_links?.length">
        <div class="col-md-6">
          <LinksList title="Internal Links" :items="analysis.internal_links" type="internal" />
        </div>
        <div class="col-md-6">
          <LinksList title="External Links" :items="analysis.external_links" type="external" />
        </div>
      </div>
    </section>
  </div>
</template>

<style scoped>
.sticky-top {
  position: sticky;
  top: 0;
  z-index: 1020;
}
</style>
