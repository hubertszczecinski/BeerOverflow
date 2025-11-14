<script setup>
import TopNavBar from '@/components/TopNavBar.vue'
import MainNavBar from '@/components/MainNavBar.vue'
import Footer from '@/components/Footer.vue'
import FlashMessages from '@/components/FlashMessages.vue'
import PhotoCaptureUploader from "@/components/PhotoCaptureUploader.vue";
import VoiceRecord from "@/components/VoiceRecord.vue";
import {useRoute, useRouter} from "vue-router";
import {provide, ref} from "vue";

// Get the router instance
const router = useRouter()
const route = useRoute()

// Provide the router to all child components
provide('router', router)

const currentUser = ref(null)
const flashMessages = ref([])

</script>

<template>
  <div id="app" class="min-h-screen flex flex-col">
    <PhotoCaptureUploader  />
    <!-- Fixed navbar at the very top -->
    <TopNavBar :user="currentUser" class="fixed top-0 left-0 right-0 z-50"/>

    <!-- Main content area that grows to fill space -->
    <div class="flex-1 flex flex-col mt-20"> <!-- mt-20 accounts for fixed TopNavBar -->

      <!-- Navigation section -->
      <MainNavBar />

      <!-- Flash messages - will now properly be below MainNavBar -->
      <FlashMessages :messages="flashMessages" class="mt-4" />

      <!-- Route outlet -->
      <main class="flex-1">
        <RouterView />
      </main>

    </div>

    <!-- Footer at the bottom -->
    <VoiceRecord/>
    <Footer />
  </div>
</template>

<style scoped>
/* Optional: Ensure smooth scrolling */
html {
  scroll-behavior: smooth;
}
</style>