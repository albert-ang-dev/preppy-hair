<script setup>
import { createClient } from '@supabase/supabase-js';

const config = useRuntimeConfig();
const supabase = createClient(config.public.supabaseUrl, config.public.supabaseKey);

const days = [
  { key: 'monday', label: 'Monday' },
  { key: 'tuesday', label: 'Tuesday' },
  { key: 'wednesday', label: 'Wednesday' },
  { key: 'thursday', label: 'Thursday' },
  { key: 'friday', label: 'Friday' },
  { key: 'saturday', label: 'Saturday' },
  { key: 'sunday', label: 'Sunday' },
]

const availability = reactive(
  Object.fromEntries(days.map((d) => [d.key, { start_time: '', end_time: '' }]))
)

const loading = ref(false)
const saving = ref(false)
const saveMessage = ref('')

onMounted(async () => {
  loading.value = true
  const { data, error } = await supabase.from('barber_availability').select('*')
  if (error) {
    console.error('Error loading availability:', error)
  } else {
    for (const row of data) {
      if (availability[row.day_of_week]) {
        availability[row.day_of_week].start_time = row.start_time?.slice(0, 5) ?? ''
        availability[row.day_of_week].end_time = row.end_time?.slice(0, 5) ?? ''
      }
    }
  }
  loading.value = false
})

async function saveAvailability() {
  saving.value = true
  saveMessage.value = ''

  const rows = days.map((d) => ({
    day_of_week: d.key,
    start_time: availability[d.key].start_time || null,
    end_time: availability[d.key].end_time || null,
  }))

  const { error } = await supabase.from('barber_availability').upsert(rows, { onConflict: 'day_of_week' })

  if (error) {
    console.error('Error saving availability:', error)
    saveMessage.value = 'Failed to save availability.'
  } else {
    saveMessage.value = 'Availability saved.'
  }
  saving.value = false
}
</script>

<template>
  <div class="bh-card p-5">
    <div class="topbar-eyebrow text-uppercase fw-semibold mb-2">Welcome back</div>
    <h1 class="brand-font display-6 fw-semibold mb-3">Ready for today's clients?</h1>
    <p class="text-muted mb-4" style="max-width: 32rem;">
      Use the sidebar to review today's schedule, check in appointments, and keep the chairs full.
    </p>

    <h4>Settings for Bookings / Appointments</h4>
    <p class="text-muted mb-4">
      You can manage your booking settings, availability, and other preferences in the settings section.
    </p>

    <div v-if="loading" class="text-muted mb-3">Loading availability…</div>

    <template v-else>
      <div v-for="day in days" :key="day.key" class="d-flex flex-wrap align-items-center gap-2 mb-2">
        <span class="availability-day-label">{{ day.label }}</span>
        <input type="time" class="form-control w-auto" v-model="availability[day.key].start_time">
        <span class="text-muted">To</span>
        <input type="time" class="form-control w-auto" v-model="availability[day.key].end_time">
      </div>

      <button
        type="button"
        class="btn btn-gold rounded-pill px-4 mt-3"
        :disabled="saving"
        @click="saveAvailability"
      >
        {{ saving ? 'Saving…' : 'Save Availability' }}
      </button>
      <p v-if="saveMessage" class="small text-muted mt-2 mb-0">{{ saveMessage }}</p>
    </template>
  </div>
</template>

<style scoped>
.availability-day-label {
  width: 100px;
}
</style>
