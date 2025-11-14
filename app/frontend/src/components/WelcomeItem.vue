<template>
  <div class="item">
    <i>
      <slot name="icon"></slot>
    </i>
    <div class="shadow-md color-red-500">
      <h3 class="`shadow:md, color-red-500` text-xl font-semibold mb-2">
        NAPIS
      </h3>
      <slot></slot>
    </div>
  </div>
</template>
