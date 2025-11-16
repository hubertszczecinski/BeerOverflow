<script setup>
import { ref, computed, onMounted, watch } from 'vue'

const question = ref('')
const file = ref(null)
const answer = ref('')
const loadingAsk = ref(false)
const error = ref('')

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api'

const products = ref([])
const selectedProductId = ref('')
const match = ref({
  cost: 0,
  length: 0,
  comfort: 0,
  overall: 0,
})
const loadingProducts = ref(false)
const loadingMatch = ref(false)
const matchError = ref('')

const selectedProduct = computed(() =>
    products.value.find(p => p.id === Number(selectedProductId.value)) || null
)

const overallPercent = computed(() =>
    Math.round((selectedProduct.value ? match.value.overall : 0) * 100)
)

const gaugeStyle = computed(() => {
  const value = selectedProduct.value ? match.value.overall : 0
  const hasValue = selectedProduct.value && value > 0
  const color = !hasValue
      ? '#d1d5db'
      : value < 0.4
          ? '#ef4444'
          : value <= 0.7
              ? '#facc15'
              : '#22c55e'
  const fillDeg = value * 180
  return {
    background: `conic-gradient(${color} 0deg, ${color} ${fillDeg}deg, #e5e7eb ${fillDeg}deg, #e5e7eb 180deg, transparent 180deg, transparent 360deg)`,
  }
})

function getProgressColor(value) {
  if (!selectedProduct.value) return '#d1d5db'
  if (value < 0.4) return '#ef4444'
  if (value <= 0.7) return '#facc15'
  return '#22c55e'
}

function formatPercent(value) {
  if (!selectedProduct.value) return 0
  if (value == null || Number.isNaN(value)) return 0
  return Math.round(value * 100)
}

function resetMatch() {
  match.value = {
    cost: 0,
    length: 0,
    comfort: 0,
    overall: 0,
  }
}

async function fetchProducts() {
  loadingProducts.value = true
  matchError.value = ''
  try {
    const resp = await fetch(`${API_BASE_URL}/products`, {
      method: 'GET',
      credentials: 'include',
    })
    if (!resp.ok) throw new Error(`products ${resp.status}`)
    const data = await resp.json()
    products.value = Array.isArray(data) ? data : []
  } catch (e) {
    matchError.value = `Failed to load offers: ${String(e)}`
  } finally {
    loadingProducts.value = false
  }
}

watch(selectedProductId, async newVal => {
  matchError.value = ''
  resetMatch()

  const id = Number(newVal)
  if (!id || Number.isNaN(id)) return

  loadingMatch.value = true
  try {
    const resp = await fetch(`${API_BASE_URL}/compare`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ product_ids: [id] }),
      credentials: 'include',
    })
    if (!resp.ok) throw new Error(`compare ${resp.status}`)
    const data = await resp.json()
    match.value = {
      cost: data.cost ?? 0,
      length: data.length ?? 0,
      comfort: data.comfort ?? 0,
      overall: data.overall ?? 0,
    }
  } catch (e) {
    matchError.value = `Failed to calculate match: ${String(e)}`
    resetMatch()
  } finally {
    loadingMatch.value = false
  }
})

function onFileChange(e) {
  file.value = e.target.files[0] || null
}

async function ask() {
  error.value = ''
  answer.value = ''
  loadingAsk.value = true
  try {
    let pdfPath = null

    if (file.value) {
      const fd = new FormData()
      fd.append('pdf', file.value)

      const respIdx = await fetch(`${API_BASE_URL}/index-pdf`, {
        method: 'POST',
        body: fd,
        credentials: 'include',
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
    loadingAsk.value = false
  }
}

onMounted(() => {
  fetchProducts()
})
</script>

<template>
  <div class="p-4">
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <!-- LEFT: Product selector + description + PDF ask -->
      <div class="border rounded bg-white p-4 space-y-4">
        <div class="space-y-2">
          <label class="block text-sm font-medium text-gray-700">
            Select offer
          </label>
          <select
              v-model="selectedProductId"
              :disabled="loadingProducts"
              class="w-full border rounded p-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">
              {{ loadingProducts ? 'Loading offers...' : 'Choose an offer...' }}
            </option>
            <option
                v-for="product in products"
                :key="product.id"
                :value="product.id"
            >
              {{ product.name }}
            </option>
          </select>
        </div>

        <div>
          <div v-if="selectedProduct">
            <h2 class="text-lg font-semibold text-gray-900">
              {{ selectedProduct.name }}
            </h2>
            <p class="mt-1 text-sm text-gray-600">
              {{ selectedProduct.description }}
            </p>
          </div>
          <p v-else class="text-sm text-gray-500">
            Select an offer to see details.
          </p>
        </div>

        <div class="pt-4 mt-4 border-t space-y-3">
          <h3 class="text-sm font-semibold text-gray-700">
            Ask about a PDF
          </h3>
          <input
              type="file"
              accept="application/pdf"
              @change="onFileChange"
              class="block w-full text-sm text-gray-700"
          />
          <textarea
              v-model="question"
              rows="3"
              class="w-full border rounded p-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Ask about the document..."
          />
          <button
              @click="ask"
              :disabled="loadingAsk"
              class="px-4 py-2 bg-blue-600 text-white rounded text-sm disabled:opacity-60 disabled:cursor-not-allowed"
          >
            {{ loadingAsk ? 'Asking...' : 'Ask' }}
          </button>

          <div v-if="error" class="text-red-600 text-sm mt-1">
            {{ error }}
          </div>
          <pre
              v-if="answer"
              class="mt-2 whitespace-pre-wrap text-sm bg-gray-50 border rounded p-2"
          >
{{ answer }}</pre>
        </div>
      </div>

      <!-- RIGHT: Match panel -->
      <div class="border rounded bg-white p-4 space-y-4">
        <h2 class="text-lg font-semibold text-gray-900">
          Match
        </h2>

        <div v-if="loadingMatch" class="text-xs text-gray-500">
          Calculating match...
        </div>

        <div v-else class="space-y-6">
          <!-- Circular Progress Bars -->
          <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
            <!-- Cost -->
            <div class="flex flex-col items-center">
              <ve-progress
                  :progress="selectedProduct ? match.cost : 0"
                  :size="120"
                  :thickness="8"
                  :emptyThickness="4"
                  :color="getProgressColor(match.cost)"
                  emptyColor="#e5e7eb"
                  :angle="-90"
                  animation="default 1000 400"
                  lineMode="out 5"
                  fontSize="1.5rem"
                  fontColor="#374151"
                  dash="strict 100 0"
              >
                <span class="text-gray-900 font-medium">
                  {{ selectedProduct ? formatPercent(match.cost) : '--' }}%
                </span>
              </ve-progress>
              <div class="mt-2 text-sm font-medium text-gray-700">Cost</div>
            </div>

            <!-- Length -->
            <div class="flex flex-col items-center">
              <ve-progress
                  :progress="selectedProduct ? match.length : 0"
                  :size="120"
                  :thickness="8"
                  :emptyThickness="4"
                  :color="getProgressColor(match.length)"
                  emptyColor="#e5e7eb"
                  :angle="-90"
                  animation="default 1000 400"
                  lineMode="out 5"
                  fontSize="1.5rem"
                  fontColor="#374151"
                  dash="strict 100 0"
              >
                <span class="text-gray-900 font-medium">
                  {{ selectedProduct ? formatPercent(match.length) : '--' }}%
                </span>
              </ve-progress>
              <div class="mt-2 text-sm font-medium text-gray-700">Length</div>
            </div>

            <!-- Comfort -->
            <div class="flex flex-col items-center">
              <ve-progress
                  :progress="selectedProduct ? match.comfort : 0"
                  :size="120"
                  :thickness="8"
                  :emptyThickness="4"
                  :color="getProgressColor(match.comfort)"
                  emptyColor="#e5e7eb"
                  :angle="-90"
                  animation="default 1000 400"
                  lineMode="out 5"
                  fontSize="1.5rem"
                  fontColor="#374151"
                  dash="strict 100 0"
              >
                <span class="text-gray-900 font-medium">
                  {{ selectedProduct ? formatPercent(match.comfort) : '--' }}%
                </span>
              </ve-progress>
              <div class="mt-2 text-sm font-medium text-gray-700">Comfort</div>
            </div>
          </div>

          <!-- Overall Match Gauge -->
          <div class="flex flex-col items-center justify-center mt-4">
            <div class="relative w-40 h-20 overflow-hidden">
              <div
                  class="absolute inset-0 w-40 h-40 rounded-full -top-20 transition-all duration-500"
                  :style="gaugeStyle"
              ></div>
              <div
                  class="absolute left-1/2 top-0 -translate-x-1/2 w-32 h-16 bg-white rounded-b-full border-t border-gray-200"
              ></div>
            </div>
            <div class="mt-2 text-lg font-semibold text-gray-900">
              {{ overallPercent }} %
            </div>
            <div class="text-xs text-gray-500">
              Overall match
            </div>
          </div>
        </div>

        <div v-if="matchError" class="text-sm text-red-600 mt-2">
          {{ matchError }}
        </div>
      </div>
    </div>
  </div>
</template>