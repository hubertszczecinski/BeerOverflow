<template>
  <div class="user-photo-container">
    <img
        v-if="photoUrl"
        :src="photoUrl"
        :alt="`User photo`"
        :class="['user-photo', sizeClass]"
        @error="handleImageError"
    />
    <div v-else :class="['user-photo-placeholder', sizeClass]">
      <i class="fas fa-user"></i>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';

const props = defineProps({
  size: {
    type: String,
    default: 'medium',
    validator: (v) => ['small', 'medium', 'large'].includes(v)
  }
});

const photoUrl = ref(null);
const sizeClass = computed(() => `size-${props.size}`);

const loadPhoto = async () => {
  try {
    const response = await fetch('/api/photo', { credentials: 'include' });
    if (response.ok) {
      const blob = await response.blob();
      photoUrl.value = URL.createObjectURL(blob);
    }
  } catch (e) {
    console.error('Photo load error:', e);
  }
};

const handleImageError = () => { photoUrl.value = null; };

onMounted(loadPhoto);
</script>

<style scoped>
.user-photo-container { display: inline-block; }
.user-photo, .user-photo-placeholder {
  border-radius: 50%;
  object-fit: cover;
  display: flex; align-items: center; justify-content: center;
}
.user-photo-placeholder { background-color: #e9ecef; color: #6c757d; }
.size-small { width: 40px; height: 40px; font-size: 20px; }
.size-medium { width: 80px; height: 80px; font-size: 40px; }
.size-large { width: 150px; height: 150px; font-size: 75px; }
</style>