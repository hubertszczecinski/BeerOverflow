<script setup>
import Actionboxes from '@/components/Actionboxes.vue'
</script>

<template>
  <div>
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
  </div>
</template>

<style scoped>
</style>
