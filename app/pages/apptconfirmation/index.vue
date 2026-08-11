<script setup>
definePageMeta({ layout: 'blank' })

const route = useRoute();
const supabase = useSupabase()

const apptId = route.query.apptid;
const confirming = ref(true)
const confirmed = ref(false)
const deleted = ref(false)
const errorMessage = ref('')

onMounted(async () => {
    if (!apptId) {
        errorMessage.value = 'Missing appointment reference.'
        confirming.value = false
        return
    }

    const { data: appt, error: fetchError } = await supabase
        .from('appointments')
        .select('status')
        .eq('id', apptId)
        .maybeSingle()

    if (fetchError || !appt) {
        confirming.value = false
        errorMessage.value = 'We couldn\'t find this appointment.'
        return
    }

    if (appt.status === 5) {
        confirming.value = false
        deleted.value = true
        return
    }

    const { error } = await supabase.from('appointments').update({ status: 1 }).eq('id', apptId)

    confirming.value = false
    if (error) {
        console.error('Error confirming appointment:', error)
        errorMessage.value = 'We couldn\'t confirm your appointment. Please contact the shop directly.'
    } else {
        confirmed.value = true
    }
})
</script>

<template>
  <div class="confirmation-page d-flex align-items-center justify-content-center">
    <div class="bh-card p-5 confirmation-card text-center">
      <div class="sidebar-mark d-flex align-items-center justify-content-center mb-3 mx-auto">
        <i class="bi bi-scissors"></i>
      </div>
      <div class="topbar-eyebrow text-uppercase fw-semibold mb-4">Preppy Hair Studio</div>

      <div v-if="confirming" class="text-muted">Confirming your appointment…</div>

      <template v-else-if="confirmed">
        <h1 class="brand-font fs-3 fw-semibold mb-2">You're confirmed!</h1>
        <p class="text-muted mb-0">See you soon.</p>
      </template>

      <template v-else-if="deleted">
        <h1 class="brand-font fs-3 fw-semibold mb-2">Appointment was marked deleted</h1>
      </template>

      <template v-else>
        <h1 class="brand-font fs-3 fw-semibold mb-2">Something went wrong</h1>
        <p class="text-muted mb-0">{{ errorMessage }}</p>
      </template>
    </div>
  </div>
</template>

<style scoped>
.confirmation-page {
  min-height: 100vh;
  background-color: var(--bh-bg);
  padding: 1.5rem;
}

.confirmation-card {
  width: 100%;
  max-width: 400px;
}
</style>