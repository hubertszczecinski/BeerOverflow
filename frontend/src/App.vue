<script setup>
import TopNavBar from '@/components/TopNavBar.vue'
import MainNavBar from '@/components/MainNavBar.vue'
import Footer from '@/components/Footer.vue'
import FlashMessages from '@/components/FlashMessages.vue'
import flashMessages from "@/components/FlashMessages.vue";
import Actionboxes from '@/components/Actionboxes.vue'
import PhotoCaptureUploader from "@/components/PhotoCaptureUploader.vue";
</script>

<template>
  <div id="app">
    <TopNavBar :user="currentUser" class="fixed top-0 z-50"/>

    <MainNavBar class=""/>

    <FlashMessages :messages="flashMessages" class="" />

    <Actionboxes class="grid grid-cols-1 md:grid-cols-2 gap-4 p-4 rounded-lg"></Actionboxes>
    <main class="main-content">
      <PhotoCaptureUploader  />
      <div class="filler-content">
        Lorem ipsum dolor sit amet, consectetur adipiscing elit. Vestibulum rutrum libero enim, eget consequat justo venenatis non. Sed mauris tellus, vehicula non tincidunt id, lacinia ornare mauris. Donec rhoncus, sapien sed vestibulum ornare, sapien dolor luctus justo, id pulvinar ex lorem ut velit. Vivamus sollicitudin turpis eget volutpat blandit. Integer et lectus eget leo suscipit ullamcorper vitae vitae ipsum. Aliquam at ex arcu. Nunc in euismod sapien, eu scelerisque ante. Etiam at nibh ac velit varius imperdiet ac ac ligula.
        Nulla nec metus quam. Cras pellentesque vulputate maximus. Nunc vitae auctor enim. Vestibulum viverra pharetra cursus. Vestibulum iaculis orci et eros facilisis auctor. Integer quis tortor sit amet velit mollis condimentum sit amet faucibus dolor. Proin semper dictum est a convallis. Nam tristique vestibulum gravida. Aenean ac convallis est. Nullam finibus, nibh eu pulvinar malesuada, metus lorem finibus sem, ut elementum tellus turpis at nunc.
        Vivamus viverra finibus velit, in cursus massa vestibulum et. Aliquam ac tincidunt nisl, eu feugiat massa. Pellentesque viverra libero metus, vel convallis libero congue vel. Curabitur tempor pretium turpis, ac porttitor orci imperdiet eu. Donec ut luctus risus. Etiam eu gravida arcu. Donec ultrices orci efficitur pellentesque rutrum. Maecenas aliquam ac purus vel imperdiet. Vivamus non erat urna. Mauris in tincidunt lacus. Curabitur dictum augue sit amet mauris blandit, ut placerat arcu luctus.
        Praesent sagittis bibendum mollis. Fusce pulvinar elit lacinia, luctus tellus id, rhoncus lectus. Proin accumsan lectus sit amet ligula imperdiet tincidunt. Aenean malesuada diam neque, aliquam ultricies est varius vel. Pellentesque habitant morbi tristique senectus et netus et malesuada fames ac turpis egestas. Donec efficitur massa felis, consequat pulvinar mauris tristique ut. Etiam non dui in tortor bibendum ultricies.
        Nulla erat risus, laoreet eu orci at, facilisis rhoncus dui. Quisque eleifend at odio a mollis. Quisque cursus ac nunc auctor aliquet. Cras interdum consequat augue, a venenatis neque tempus lobortis. Donec et molestie massa. Phasellus nec ligula vitae diam finibus auctor. Curabitur commodo ante vitae augue laoreet, at lobortis est congue. Nam ac eros auctor, consequat velit et, laoreet lacus. Donec auctor lobortis lacus, ac accumsan lorem vulputate eget. Quisque aliquet nisl ut nibh iaculis, eget accumsan erat sagittis. Nunc consectetur quis nunc eu scelerisque. Pellentesque ut justo non velit malesuada aliquam ut id erat. Morbi laoreet euismod velit sit amet tempus. Quisque ligula ligula, facilisis posuere dictum a, laoreet vitae nunc. Nullam ac pharetra justo, et molestie lacus. Donec ac tincidunt elit.
      </div>
    </main>
  <Footer/>
  </div>

</template>

<style scoped>

</style>
