<template>
  <div class="background-div">
  <div class="hero-banner">
    <!-- Background div -->


    <div class="container">
      <h1 ref="typewriterHeader" class="typewriter-header">The Bank by Your Side</h1>
      <p class="subtitle">Modern banking solutions for you</p>

      <template v-if="!authStore.isLoggedIn">
        <router-link to="/register" class="btn btn-primary btn-lg me-3 rounded-pill" style="border: 1px solid #000;">
          <i class="fas fa-user-plus"></i> Open Account
        </router-link>
        <router-link to="/login" class="btn btn-outline-primary btn-lg rounded-pill" style="color:black; border: 1px solid #000;">
          <i class="fas fa-sign-in-alt"></i> Login
        </router-link>
      </template>

      <template v-else>
        <router-link to="/dashboard" class="btn btn-primary btn-lg rounded-pill">
          <i class="fas fa-home"></i> Go to Dashboard
        </router-link>
      </template>
    </div>


  </div>
  </div>
  <VoiceNavBox />
</template>

<script setup>
import { useAuthStore } from '@/stores/auth';
import VoiceNavBox from '@/components/VoiceNavBox.vue';
import { ref, onMounted, onBeforeUnmount, watch } from 'vue';
import { useRoute } from 'vue-router';

const authStore = useAuthStore();
const route = useRoute();
const typewriterHeader = ref(null);
let animationInterval = null;

const text = "The Bank by Your Side";
const speed = 70; // ms na literę

// Funkcja uruchamiająca animację
function startTypewriterEffect() {
  const header = typewriterHeader.value;
  if (!header) return;

  // Czyścimy poprzednią animację
  clearTimeout(animationInterval);
  header.innerHTML = '';
  header.classList.remove('typing-complete');

  const letters = [];
  let index = 0;

  // Tworzymy spany
  for (let char of text) {
    const span = document.createElement('span');
    span.className = 'letter';
    span.textContent = char === ' ' ? '\u00A0' : char;
    span.style.opacity = '0';
    header.appendChild(span);
    letters.push(span);
  }

  // Rozpocznij animację
  function type() {
    if (index < letters.length) {
      letters[index].style.opacity = '1';
      letters[index].style.transition = 'opacity 0.1s ease';
      index++;
      animationInterval = setTimeout(type, speed);
    } else {
      header.classList.add('typing-complete');
      // Pokaż podtytuł
      const subtitle = document.querySelector('.subtitle');
      if (subtitle) {
        setTimeout(() => subtitle.classList.add('show'), 200);
      }
    }
  }

  type();
}

// Obserwuj zmianę trasy
watch(
    () => route.path,
    (newPath) => {
      if (newPath === '/' || newPath === '/home') {
        // Małe opóźnienie, by DOM się ustabilizował
        setTimeout(startTypewriterEffect, 100);
      } else {
        // Czyść animację przy wyjściu
        const header = typewriterHeader.value;
        if (header) {
          header.innerHTML = text; // przywróć oryginalny tekst
          header.classList.remove('typing-complete');
          document.querySelector('.subtitle')?.classList.remove('show');
        }
      }
    },
    { immediate: true }
);

onBeforeUnmount(() => {
  clearTimeout(animationInterval);
});
</script>

<style scoped>
.hero-banner {
  position: relative;
  min-height: 100vh; /* Ensure it stretches at least to viewport height */
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.background-div {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: yellow;
  z-index: -50;
}

.typewriter-header {
  font-size: 4.5rem;
  font-weight: 700;
  display: inline-block;
  overflow: hidden;
  white-space: nowrap;
}

.letter {
  display: inline-block;
  opacity: 0;
  transition: opacity 0.1s ease;
}

/* Po zakończeniu – opcjonalnie możesz dodać klasę dla efektu */
.typing-complete .letter {
  opacity: 1;
}

/* Podtytuł */
.subtitle {
  opacity: 0;
  transform: translateY(20px);
  transition: all 0.6s ease;
  font-size: 1.3rem;
  margin-top: 1rem;
}

.subtitle.show {
  opacity: 1;
  transform: translateY(0);
}

/* Responsywne */
@media (max-width: 768px) {
  .typewriter-header {
    font-size: 2.5rem;
  }
}

@media (max-width: 480px) {
  .typewriter-header {
    font-size: 2rem;
  }
}
</style>