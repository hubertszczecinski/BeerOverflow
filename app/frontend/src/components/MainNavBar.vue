<script setup>

</script>


<template>
  <div class="component-container text-gray-950 bg-gray-700 border-gray-200">
    <ul class="horizontal-list">
      <li>
        <div>
          <a href="www.cmz.com">Account & Cards</a>
        </div>
      </li>

      <li>
        <div>
          <a href="www.google.com">Saving & Investments</a>
        </div>
      </li>

      <li>
        <div>
          <a href="127.0.0.1:5173/">My Account</a>
        </div>

      </li>
      <li>
        <div><a href="www.whatever.com">Loan & Financing</a></div>
      </li>
      <li>
        <div><a href="www.whatever.com">...</a></div>
      </li>
      <li>
        <div><a href="www.whatever.com">...</a></div>
      </li>
      <li>
        <div><a href="www.whatever.com">Magazine</a></div>
      </li>
    </ul>

  </div>
</template>


<style scoped>
.component-container {
  height: 100px;
  width: 100%;
}

.horizontal-list {
  display: flex;
  gap: 1rem;
  list-style-type:none;
  margin-block-start: 0em;
  margin-block-end: 0em;
  padding-inline-start: 40px;
  align-items: center;
  height: 100%;
}

/* Make logo container specific height */
.horizontal-list li:first-child div {
  height: 80px; /* Control logo container height */
  display: flex;
  align-items: center;
}

.horizontal-list li div img {
  height: 80%;
}

.horizontal-list a {
  color: white;
  text-decoration: none;
}

.horizontal-list a:hover {
  filter: brightness(2)
}


.horizontal-list li div:hover {
  transform: translateY(-1px);
}
</style>