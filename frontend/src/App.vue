<script setup>
import TopNavBar from '@/components/TopNavBar.vue'
import MainNavBar from '@/components/MainNavBar.vue'
import Footer from '@/components/Footer.vue'
import FlashMessages from '@/components/FlashMessages.vue'
import Actionboxes from '@/components/Actionboxes.vue'
import PhotoCaptureUploader from "@/components/PhotoCaptureUploader.vue";
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

      <!-- Main content that can scroll -->
      <main class="flex-1">
        <Actionboxes class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 p-4 rounded-lg"/>
        <!-- Two divs in a row -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6 p-4">
          <!-- Left column -->
          <div class="bg-white rounded-lg shadow-md p-6">
            <h2 class="text-xl font-bold mb-4">Left Content</h2>
            <p class="text-gray-700">
              Lorem ipsum dolor sit amet, consectetur adipiscing elit. Vestibulum rutrum libero enim, eget consequat justo venenatis non. Sed mauris tellus, vehicula non tincidunt id, lacinia ornare mauris.
            </p>
            <!-- Add more content as needed -->
          </div>

          <!-- Right column -->
          <div class="bg-white rounded-lg shadow-md p-6">
            <h2 class="text-xl font-bold mb-4">Right Content</h2>
            <p class="text-gray-700">
              Donec rhoncus, sapien sed vestibulum ornare, sapien dolor luctus justo, id pulvinar ex lorem ut velit. Vivamus sollicitudin turpis eget volutpat blandit. Integer et lectus eget leo suscipit ullamcorper.
            </p>
            <!-- Add more content as needed -->
          </div>
        </div>
      </main>

    </div>

    <!-- Footer at the bottom -->
    <Footer />
  </div>
</template>

<style scoped>
/* Optional: Ensure smooth scrolling */
html {
  scroll-behavior: smooth;
}
</style>