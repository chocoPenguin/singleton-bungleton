<script setup lang="ts">
import TheWelcome from '@/components/TheWelcome.vue'
import Button from 'primevue/button'
</script>

<template>
  <main>
    <div class="card flex justify-center" style="margin: 20px 0;">
        <Button label="Verify" />
    </div>
    <TheWelcome />
  </main>
</template>