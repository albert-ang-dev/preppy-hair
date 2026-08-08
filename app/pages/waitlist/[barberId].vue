<script setup>
import { createClient } from '@supabase/supabase-js'
import Swal from 'sweetalert2'

const config = useRuntimeConfig();
const supabase = createClient(config.public.supabaseUrl, config.public.supabaseKey);
const route = useRoute();

definePageMeta({ layout: 'blank' })
onMounted(async () => {
  const linked = route.params.barberId;
  const customerId = route.query.customerId;
  console.log('Barber ID from route:', linked);
  console.log('Customer ID from query:', customerId);

})

</script>


<template>
  <div class="waitlist-page d-flex align-items-center justify-content-center">
    <div class="bh-card p-5 waitlist-card text-center">
      <div class="sidebar-mark d-flex align-items-center justify-content-center mb-3 mx-auto">
        <i class="bi bi-scissors"></i>
      </div>
      <div class="topbar-eyebrow text-uppercase fw-semibold mb-4">Preppy Hair Studio</div>

      <p class="text-muted small mb-1">Barber</p>
      <h2 class="brand-font fs-4 fw-semibold mb-4">Marco Reyes</h2>

      <p class="text-muted small mb-1">Client</p>
      <h2 class="brand-font fs-4 fw-semibold mb-4">Juan Dela Cruz</h2>

      <p class="text-muted small mb-1">Your position in line</p>
      <div class="waitlist-position">3</div>
    </div>
  </div>
</template>

<style scoped>
.waitlist-page {
  min-height: 100vh;
  background-color: var(--bh-bg);
  padding: 1.5rem;
}

.waitlist-card {
  width: 100%;
  max-width: 400px;
}

.waitlist-position {
  font-family: 'Playfair Display', Georgia, serif;
  font-size: 3rem;
  font-weight: 700;
  color: var(--bh-gold-dark);
}
</style>