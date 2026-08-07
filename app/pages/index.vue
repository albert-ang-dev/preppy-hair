<script setup>
import { createClient } from '@supabase/supabase-js';

const config = useRuntimeConfig();
const supabase = createClient(config.public.supabaseUrl, config.public.supabaseKey);
const appointmentLink = ref("localhost:3000/book/");

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
  Object.fromEntries(days.map((d) => [d.key, { start_time: '', end_time: '', closed: false }]))
)

const loading = ref(false)
const saving = ref(false)
const saveMessage = ref('')

onMounted(async () => {
  loading.value = true
  const { data: { user } } = await supabase.auth.getUser()
  const { data, error } = await supabase
    .from('barber_availability')
    .select('*')
    .eq('barber_id', user.id)

  if (error) {
    console.error('Error loading availability:', error)
  } else {
    appointmentLink.value += user.id;
    for (const row of data) {
      if (availability[row.day_of_week]) {
        availability[row.day_of_week].start_time = row.start_time?.slice(0, 5) ?? ''
        availability[row.day_of_week].end_time = row.end_time?.slice(0, 5) ?? ''
        availability[row.day_of_week].closed = !row.start_time || !row.end_time
      }
    }
  }
  loading.value = false
})

async function saveAvailability() {
  saving.value = true
  saveMessage.value = ''

  const { data: { user } } = await supabase.auth.getUser()

  const rows = days.map((d) => ({
    barber_id: user.id,
    day_of_week: d.key,
    start_time: availability[d.key].closed ? null : availability[d.key].start_time || null,
    end_time: availability[d.key].closed ? null : availability[d.key].end_time || null,
  }))

  const { error } = await supabase
    .from('barber_availability')
    .upsert(rows, { onConflict: 'barber_id,day_of_week' })

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


  </div>
</template>

<style scoped>
.availability-day-label {
  width: 100px;
}
</style>
