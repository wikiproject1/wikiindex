<script setup>
import { ref } from 'vue'
import axios from 'axios'
import SearchBar from './components/SearchBar.vue'
import ArticleCard from './components/ArticleCard.vue'
import AnalysisPanel from './components/AnalysisPanel.vue'
import LinksList from './components/LinksList.vue'
import Recommendations from './components/Recommendations.vue'


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
const recommendations = ref([])

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
    recommendations.value = []

    // Fetch article summary from Wikipedia REST API (try Swahili first, then English)
    let summaryRes
    let data
    
    try {
      summaryRes = await axios.get(
        `https://sw.wikipedia.org/api/rest_v1/page/summary/${encodeURIComponent(title)}`
      )
      data = summaryRes.data
    } catch (e) {
      console.warn('Swahili Wikipedia failed, trying English:', e)
      try {
        summaryRes = await axios.get(
          `https://en.wikipedia.org/api/rest_v1/page/summary/${encodeURIComponent(title)}`
        )
        data = summaryRes.data
      } catch (e2) {
        throw new Error('Article not found in Swahili or English Wikipedia')
      }
    }
    
    if (!data || !data.extract) {
      throw new Error('No article content found')
    }
    
    article.value.title = data.title || title
    article.value.summary = data.extract || ''
    article.value.url = data.content_urls?.desktop?.page || data.content_urls?.mobile?.page || ''

    // Fetch detailed data using MediaWiki Action API
    const pageTitle = data.title || title
    const wikiLang = data.lang || 'sw' // Use the language from the summary response
    const wikiBase = wikiLang === 'sw' ? 'https://sw.wikipedia.org' : 'https://en.wikipedia.org'
    
    // Fetch categories, links, and other metadata with error handling
    let categories = []
    let internalLinks = []
    let externalLinks = []
    
    try {
      const categoriesRes = await axios.get(`${wikiBase}/w/api.php`, {
        params: {
          action: 'query',
          format: 'json',
          formatversion: 2,
          titles: pageTitle,
          prop: 'categories',
          clshow: '!hidden',
          cllimit: 'max'
        }
      })
      console.log('Categories response:', categoriesRes.data)
      const pages = categoriesRes.data.query?.pages || []
      if (pages.length > 0) {
        const page = pages[0]
        if (page.categories) {
          categories = page.categories.map(cat => cat.title.replace('Category:', ''))
        }
      }
    } catch (e) {
      console.warn('Failed to fetch categories:', e)
      categories = []
    }
    
    try {
      const linksRes = await axios.get(`${wikiBase}/w/api.php`, {
        params: {
          action: 'query',
          format: 'json',
          formatversion: 2,
          titles: pageTitle,
          prop: 'links',
          plnamespace: 0,
          pllimit: 'max'
        }
      })
      console.log('Links response:', linksRes.data)
      const pages = linksRes.data.query?.pages || []
      if (pages.length > 0) {
        const page = pages[0]
        if (page.links) {
          internalLinks = page.links.map(link => link.title)
        }
      }
    } catch (e) {
      console.warn('Failed to fetch internal links:', e)
      internalLinks = []
    }
    
    try {
      const extlinksRes = await axios.get(`${wikiBase}/w/api.php`, {
        params: {
          action: 'query',
          format: 'json',
          formatversion: 2,
          titles: pageTitle,
          prop: 'extlinks',
          ellimit: 'max'
        }
      })
      console.log('External links response:', extlinksRes.data)
      const pages = extlinksRes.data.query?.pages || []
      if (pages.length > 0) {
        const page = pages[0]
        if (page.extlinks) {
          externalLinks = page.extlinks.map(link => link['*'])
        }
      }
    } catch (e) {
      console.warn('Failed to fetch external links:', e)
      externalLinks = []
    }



    // Analyze categories for birth/death years and other metadata
    const birthYear = extractBirthYear(categories)
    const { isDead, deathYear } = extractDeathYear(categories)
    const isLiving = detectLiving(categories)
    const isStub = detectStub(categories)
    
    // Calculate AI content risk
    const aiRisk = estimateAIContentRisk(article.value.summary)
    
    // Calculate trust score based on content quality
    score.value = calculateTrustScore(article.value.summary, categories, internalLinks.length, externalLinks.length)

    // Build analysis object with REAL data
    analysis.value = {
      ai_content_risk: aiRisk,
      broken_links_count: 0, // We'll implement this later
      broken_external_links: [],
      content_type: 'article',
      total_links_internal: internalLinks.length,
      total_links_external: externalLinks.length,
      internal_links: internalLinks,
      external_links: externalLinks,
      categories: categories,
      is_living: isLiving,
      is_dead: isDead,
      death_year: deathYear,
      birth_year: birthYear,
      is_stub: isStub,
      ai_explanation: generateAIExplanation(article.value.summary, categories, internalLinks.length, externalLinks.length, aiRisk, isStub, isLiving, isDead, birthYear, deathYear)
    }

    recommendations.value = buildRecommendations(analysis.value, article.value)
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

function buildRecommendations(a, art) {
  const recs = []
  if (a.is_stub) {
    recs.push('Makala imewekwa kama mbegu (stub) — ongeza maudhui na marejeo ya kuaminika.')
  }
  if (a.total_links_external <= 0) {
    recs.push('Haina marejeo ya nje — ongeza vyanzo vya kuaminika.')
  } else if (a.total_links_external < 3) {
    recs.push(`Marejeo machache (${a.total_links_external}) — ongeza citations zaidi.`)
  }
  if (a.broken_links_count > 0) {
    recs.push(`Rekebisha viungo vilivyovunjika (${a.broken_links_count}).`)
  }
  if (a.total_links_internal < 5) {
    recs.push('Ongeza viungo vya ndani kwa makala zinazohusiana.')
  }
  if (typeof a.ai_content_risk === 'number') {
    if (a.ai_content_risk >= 0.7) {
      recs.push('Hatari kubwa ya mtindo wa AI — punguza maneno ya jumla, ongeza ushahidi.')
    } else if (a.ai_content_risk >= 0.4) {
      recs.push('Hatari ya kati ya mtindo wa AI — pitia uandishi na usomekeaji.')
    }
  }
  if ((art.summary || '').length < 200) {
    recs.push('Muhtasari ni mfupi — boresha dibaji (lead section).')
  }
  return recs
}

// Helper functions for data analysis
function extractBirthYear(categories) {
  for (const cat of categories) {
    const match = cat.match(/(?:Waliozaliwa|Kuzaliwa)\s+(\d{3,4})$/i)
    if (match) {
      const year = parseInt(match[1])
      if (year >= 1000 && year <= 2100) return year
    }
  }
  return null
}

function extractDeathYear(categories) {
  for (const cat of categories) {
    const match = cat.match(/(?:Waliofariki|Vifo vya)\s+(\d{3,4})$/i)
    if (match) {
      const year = parseInt(match[1])
      if (year >= 1000 && year <= 2100) return { isDead: true, deathYear: year }
    }
  }
  return { isDead: false, deathYear: null }
}

function detectLiving(categories) {
  const livingPatterns = [/watu hai/i, /walio hai/i, /living people/i]
  return categories.some(cat => livingPatterns.some(pattern => pattern.test(cat)))
}

function detectStub(categories) {
  return categories.some(cat => /mbegu|stub/i.test(cat))
}

function estimateAIContentRisk(text) {
  if (!text) return 0.0
  const patterns = [
    /as an ai language model/i,
    /in conclusion,/i,
    /this article aims to/i,
    /it is important to note that/i,
  ]
  const hits = patterns.reduce((count, pattern) => count + (pattern.test(text) ? 1 : 0), 0)
  const lengthPenalty = text.length < 200 ? 0.0 : Math.min(0.3, text.length / 5000)
  return Math.min(1.0, hits * 0.25 + lengthPenalty)
}

function calculateTrustScore(summary, categories, internalLinks, externalLinks) {
  let score = 50 // Base score
  
  // Bonus for longer summary
  if (summary.length > 200) score += 10
  if (summary.length > 500) score += 10
  
  // Bonus for more internal links
  if (internalLinks > 10) score += 10
  if (internalLinks > 20) score += 10
  
  // Bonus for external links
  if (externalLinks > 0) score += 10
  if (externalLinks > 5) score += 10
  
  // Penalty for stub
  if (categories.some(cat => /mbegu|stub/i.test(cat))) score -= 15
  
  return Math.max(0, Math.min(100, score))
}

function generateAIExplanation(summary, categories, internalLinks, externalLinks, aiRisk, isStub, isLiving, isDead, birthYear, deathYear) {
  const parts = []
  
  parts.push("This appears to be a standard encyclopedia article.")
  
  if (birthYear) {
    parts.push(`The subject seems to have been born in ${birthYear}.`)
  }
  
  if (isLiving) {
    parts.push("Categories suggest the person is living.")
  }
  
  if (isDead) {
    parts.push("Categories indicate the subject is deceased.")
  }
  
  if (isStub) {
    parts.push("The article is categorized as a stub (mbegu); it may be incomplete.")
  }
  
  parts.push(`There are about ${internalLinks} internal links and ${externalLinks} external links.`)
  
  if (aiRisk >= 0.7) {
    parts.push("Text shows a high risk of AI-generated patterns.")
  } else if (aiRisk >= 0.4) {
    parts.push("Text shows a moderate risk of AI-generated patterns.")
  } else {
    parts.push("Low indications of AI-generated phrasing in summary.")
  }
  
  return parts.join(" ")
}

function loadDemoData() {
  // Load demo data for testing
  fetchWikipedia('A-Q')
}
</script>

<template>
  <div class="min-vh-100" style="background: linear-gradient(180deg, #f8f9fa 0%, #ffffff 100%);">
    <nav class="navbar navbar-light bg-white border-bottom sticky-top">
      <div class="container">
        <span class="navbar-brand mb-0 h1 d-flex align-items-center">
          <img src="https://commons.wikimedia.org/wiki/Special:FilePath/Wikimedia-logo.png" alt="Wikimedia logo" style="height:28px;width:auto" class="me-2" />
          WikiTrust Index
        </span>
      </div>
    </nav>

    <section class="container py-5 d-flex flex-column align-items-center">
      <SearchBar @analyze="fetchWikipedia" />
      <div class="mt-3">
        <button @click="loadDemoData" class="btn btn-outline-secondary btn-sm">
          <i class="bi bi-play-circle me-1"></i>Load Demo Data
        </button>
      </div>
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
        :loading="loading"
      />

      <div class="row g-3 mt-0" v-if="analysis.internal_links?.length || analysis.external_links?.length">
        <div class="col-md-6">
          <LinksList title="Internal Links" :items="analysis.internal_links" type="internal" />
        </div>
        <div class="col-md-6">
          <LinksList title="External Links" :items="analysis.external_links" type="external" />
        </div>
      </div>

      <div class="row g-3 mt-0">
        <div class="col-12">
          <Recommendations :items="recommendations" />
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
