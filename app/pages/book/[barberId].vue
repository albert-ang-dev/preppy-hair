<script setup>
import { createClient } from '@supabase/supabase-js'
import Swal from 'sweetalert2'

definePageMeta({ layout: 'blank' })

const config = useRuntimeConfig()
const supabase = createClient(config.public.supabaseUrl, config.public.supabaseKey)

const route = useRoute()
const barberId = route.params.barberId

const dayKeys = ['sunday', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday']

function toDateKey(date) {
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

const todayDate = toDateKey(new Date())
const maxBookableDate = toDateKey(new Date(new Date().setDate(new Date().getDate() + 7)))

const form = reactive({
  client_name: '',
  client_email: '',
  service: '',
  appointment_date: '',
  appointment_time: '',
})

const availableSlots = ref([])
const loadingSlots = ref(false)
const submitting = ref(false)
const booked = ref(false)

function generateSlots(start, end, stepMinutes) {
  const slots = []
  let [h, m] = start.split(':').map(Number)
  const [endH, endM] = end.split(':').map(Number)

  while (h < endH || (h === endH && m < endM)) {
    slots.push(`${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}`)
    m += stepMinutes
    if (m >= 60) {
      m -= 60
      h += 1
    }
  }
  return slots
}

async function onDateChange() {
  form.appointment_time = ''
  availableSlots.value = []
  if (!form.appointment_date) return

  if (form.appointment_date < todayDate || form.appointment_date > maxBookableDate) {
    form.appointment_date = ''
    Swal.fire('Invalid date', 'Please choose a date within the next 7 days.', 'warning')
    return
  }

  loadingSlots.value = true

  const [year, month, day] = form.appointment_date.split('-').map(Number)
  const dayKey = dayKeys[new Date(year, month - 1, day).getDay()]

  const { data: hours } = await supabase
    .from('barber_availability')
    .select('start_time, end_time')
    .eq('barber_id', barberId)
    .eq('day_of_week', dayKey)
    .maybeSingle()

  if (!hours?.start_time || !hours?.end_time) {
    loadingSlots.value = false
    return
  }

  const { data: existing } = await supabase
    .from('booked_slots')
    .select('appointment_time')
    .eq('barber_id', barberId)
    .eq('appointment_date', form.appointment_date)

  const taken = new Set((existing ?? []).map((row) => row.appointment_time))

  availableSlots.value = generateSlots(hours.start_time, hours.end_time, 30)
    .filter((slot) => !taken.has(slot))

  loadingSlots.value = false
}

async function submitBooking() {
  if (form.appointment_date < todayDate || form.appointment_date > maxBookableDate) {
    Swal.fire('Invalid date', 'Please choose a date within the next 7 days.', 'warning')
    return
  }

  submitting.value = true

  const { error } = await supabase.from('clients').insert({
    barber_id: barberId,
    client_name: form.client_name,
    client_email: form.client_email,
    service: form.service,
    appointment_date: form.appointment_date,
    appointment_time: form.appointment_time,
    appointment_status: 0,
  })

  submitting.value = false

  if (error) {
    Swal.fire('Booking failed', error.message, 'error')
  } else {
    booked.value = true
  }
}
</script>

<template>
  <div class="booking-page d-flex align-items-center justify-content-center">
    <div class="bh-card p-5 booking-card">
      <template v-if="!booked">
        <div class="d-flex flex-column align-items-center text-center mb-4">
          <div class="sidebar-mark d-flex align-items-center justify-content-center mb-3">
            <i class="bi bi-scissors"></i>
          </div>
          <div class="topbar-eyebrow text-uppercase fw-semibold">Preppy Hair Studio</div>
          <h1 class="brand-font fs-3 fw-semibold mb-0">Book an appointment</h1>
        </div>

        <form @submit.prevent="submitBooking">
          <div class="mb-3">
            <label class="form-label small fw-semibold">Name</label>
            <input type="text" class="form-control bh-input" v-model="form.client_name" required>
          </div>
          <div class="mb-3">
            <label class="form-label small fw-semibold">Email</label>
            <input type="email" class="form-control bh-input" v-model="form.client_email" required>
          </div>
          <div class="mb-3">
            <label class="form-label small fw-semibold">Service</label>
            <input type="text" class="form-control bh-input" v-model="form.service" required>
          </div>
          <div class="mb-3">
            <label class="form-label small fw-semibold">Date</label>
            <input
              type="date"
              class="form-control bh-input"
              v-model="form.appointment_date"
              :min="todayDate"
              :max="maxBookableDate"
              @change="onDateChange"
              required
            >
          </div>
          <div class="mb-4" v-if="form.appointment_date">
            <label class="form-label small fw-semibold">Time</label>
            <div v-if="loadingSlots" class="text-muted small">Loading available times…</div>
            <div v-else-if="availableSlots.length === 0" class="text-muted small">No slots available this day.</div>
            <select v-else class="form-control bh-input" v-model="form.appointment_time" required>
              <option value="" disabled>Select a time</option>
              <option v-for="slot in availableSlots" :key="slot" :value="slot">{{ slot }}</option>
            </select>
          </div>

          <button type="submit" class="btn btn-gold rounded-pill w-100 py-2" :disabled="submitting || !form.appointment_time">
            {{ submitting ? 'Booking…' : 'Confirm booking' }}
          </button>
        </form>
      </template>

      <template v-else>
        <h1 class="brand-font fs-3 fw-semibold mb-3">You're booked!</h1>
        <p class="text-muted mb-0">
          {{ form.service }} on {{ form.appointment_date }} at {{ form.appointment_time }}. See you then.
        </p>
      </template>
    </div>
  </div>
</template>

<style scoped>
.booking-page {
  min-height: 100vh;
  background-color: var(--bh-bg);
  padding: 1.5rem;
}

.booking-card {
  width: 100%;
  max-width: 440px;
}

.bh-input {
  border: 1px solid var(--bh-border);
  border-radius: 10px;
  padding: 0.6rem 0.85rem;
}

.bh-input:focus {
  border-color: var(--bh-gold);
  box-shadow: 0 0 0 0.2rem rgba(199, 160, 89, 0.2);
}
</style>
