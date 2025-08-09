<script setup>
import { ref } from 'vue'

const emit = defineEmits(['analyze'])
const query = ref('')

function onSubmit(e) {
  e.preventDefault()
  if (!query.value.trim()) return
  emit('analyze', query.value.trim())
}
</script>

<template>
  <form class="d-flex justify-content-center" @submit="onSubmit">
    <div class="input-group input-group-lg" style="max-width: 720px;">
      <span class="input-group-text bg-white"><i class="bi bi-search"></i></span>
      <input v-model="query" type="text" class="form-control" placeholder="Tafuta makala ya Wikipedia ya Kiswahili..." aria-label="Tafuta makala ya Wikipedia ya Kiswahili" />
      <button class="btn btn-primary" type="submit">
        Fetch & Analyze
      </button>
    </div>
  </form>
</template>

<style scoped>
</style>


