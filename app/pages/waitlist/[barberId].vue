<script setup>
import { createClient } from '@supabase/supabase-js'
import Swal from 'sweetalert2'

const config = useRuntimeConfig();
const supabase = createClient(config.public.supabaseUrl, config.public.supabaseKey);
const route = useRoute();
const positionLine = ref(null);
const customerName = ref("");
const barberName = ref("");

definePageMeta({ layout: 'blank' })
onMounted(async () => {
    const { data: barberData, error: barberError } = await supabase
        .from('preppyhair_barbers')
        .select('barber_name')
        .eq('barber_id', route.params.barberId)
        .maybeSingle();

    if (!barberError && barberData) {
        barberName.value = barberData.barber_name;
    }

    const response = await supabase.from('walkins').select('*').eq('barber_id', route.params.barberId).order('created_at', { ascending: true });
    if (response.error) {
        Swal.fire('Error', 'Failed to fetch waitlist data.', 'error');
    }else{
        const waitlistData = response.data;
        const userIndex = waitlistData.findIndex(item => item.id === route.query.appointment_id);
        if (userIndex !== -1) {
            const positionInLine = userIndex + 1; // +1 because array index starts at 0
            positionLine.value = positionInLine ;
            customerName.value = waitlistData[userIndex].client_name;
        }
    }

});

</script>


<template>
  <div class="waitlist-page d-flex align-items-center justify-content-center">
    <div class="bh-card p-5 waitlist-card text-center">
      <div class="sidebar-mark d-flex align-items-center justify-content-center mb-3 mx-auto">
        <i class="bi bi-scissors"></i>
      </div>
      <div class="topbar-eyebrow text-uppercase fw-semibold mb-4">Preppy Hair Studio</div>

      <p class="text-muted small mb-1">Barber</p>
      <h2 class="brand-font fs-4 fw-semibold mb-4">{{ barberName }}</h2>

      <p class="text-muted small mb-1">Client</p>
      <h2 class="brand-font fs-4 fw-semibold mb-4">{{ customerName }}</h2>

      <p class="text-muted small mb-1">Your position in line</p>
      <div class="waitlist-position">{{ positionLine }}</div>
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