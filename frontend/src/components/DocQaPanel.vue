<script setup>
  import { ref } from 'vue'

  const question = ref('')
  const file = ref(null)
  const answer = ref('')
  const loading = ref(false)
  const error = ref('')

  const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api'

  function onFileChange(e) {
    file.value = e.target.files[0] || null
  }

  async function ask() {
    error.value = ''
    answer.value = ''
    loading.value = true
    try {
      let pdfPath = null

      if (file.value) {
        const fd = new FormData()
        fd.append('pdf', file.value)

        const respIdx = await fetch(`${API_BASE_URL}/index-pdf`, {
          method: 'POST',
          body: fd,
          credentials: 'include', // żeby cookies z Flaska szły (auth)
        })
        if (!respIdx.ok) throw new Error(`index-pdf ${respIdx.status}`)
        const dataIdx = await respIdx.json()
        pdfPath = dataIdx.pdf_path
      }

      const payload = { question: question.value }
      if (pdfPath) payload.pdf_path = pdfPath

      const respAsk = await fetch(`${API_BASE_URL}/ask`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
        credentials: 'include',
      })
      if (!respAsk.ok) throw new Error(`ask ${respAsk.status}`)
      const dataAsk = await respAsk.json()
      answer.value = dataAsk.answer || JSON.stringify(dataAsk)
    } catch (e) {
      error.value = String(e)
    } finally {
      loading.value = false
    }
  }
  </script>

  <template>
    <div class="p-4 border rounded bg-white space-y-3">
      <input type="file" accept="application/pdf" @change="onFileChange" />
      <textarea v-model="question" rows="3" class="w-full border rounded p-2"
                placeholder="Ask about the document..." />
      <button @click="ask" :disabled="loading" class="px-4 py-2 bg-blue-600 text-white rounded">
        {{ loading ? 'Asking...' : 'Ask' }}
      </button>

      <div v-if="error" class="text-red-600 mt-2">{{ error }}</div>
      <pre v-if="answer" class="mt-2 whitespace-pre-wrap">{{ answer }}</pre>
    </div>
  </template>
