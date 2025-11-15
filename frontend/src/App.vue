<script setup>
import TopNavBar from '@/components/TopNavBar.vue'
import MainNavBar from '@/components/MainNavBar.vue'
import Footer from '@/components/Footer.vue'
import FlashMessages from '@/components/FlashMessages.vue'
import flashMessages from "@/components/FlashMessages.vue";
import Actionboxes from '@/components/Actionboxes.vue'
import PhotoCaptureUploader from "@/components/PhotoCaptureUploader.vue";
import DocQaPanel from '@/components/DocQaPanel.vue'

</script>

<template>
    <div id="app">
      <TopNavBar :user="currentUser" class="fixed top-0 z-50" />

      <MainNavBar />

      <FlashMessages :messages="flashMessages" />

      <Actionboxes class="grid grid-cols-1 md:grid-cols-2 gap-4 p-4 rounded-lg" />

      <main class="main-content p-4 space-y-6">
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <PhotoCaptureUploader />
          <DocQaPanel />
        </div>
      </main>

      <Footer />
    </div>
  </template>

<style scoped>

</style>
