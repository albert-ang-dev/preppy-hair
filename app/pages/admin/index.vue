<script setup>
/*
      [0] Waiting for confirmation
      [1] Confirm
      [2] Checked In
      [3] In-Service
      [4] No Show
      [5] Cancel
*/
import Swal from 'sweetalert2'

const supabase = useSupabase()
const currentUser = ref(null)

const walkInForm = ref({ name: '', email: '', service: '', date: '' })
const appointmentForm = ref({ name: '', email: '', service: '', date: '' })

onMounted(async () => {
  const { data: { user } } = await supabase.auth.getUser();
  currentUser.value = user;
})

function  addWalkIn(){
  if (!walkInForm.value.name || !walkInForm.value.email || !walkInForm.value.service) {
    Swal.fire('Error', 'Please fill in all fields.', 'error');
    return;
  }else{
    supabase.from('walkins').insert({
      client_name: walkInForm.value.name,
      client_email: walkInForm.value.email,
      service: walkInForm.value.service,
      barber_id: currentUser.value.id, // Replace with the actual barber ID
      status:2
    }).select().then(async({ data, error }) => {
      if (error) {
        console.error('Error adding walk-in:', error);
        Swal.fire('Error', 'Failed to add walk-in.', 'error');
      } else {
        Swal.fire('Success', 'Walk-in added successfully.', 'success');
        getWalkIns(); // Refresh the walk-ins list
        
        try {
          // Vercel routes '/api/send' directly to your 'api/send.py' script
          const response = await $fetch('/api/send', {
            method: 'POST',
            body: {
              name: walkInForm.value.name,
              email: walkInForm.value.email,
              service: walkInForm.value.service,
              barber_id: currentUser.value.id, // Replace with the actual barber ID
              client_appt_id: data.id
            }
          })

          if (response.success) {
            Swal.fire('Success', 'Notification email sent successfully.', 'success');
            // Reset form on success
            walkInForm.value = { name: '', email: '', service: '' };
          }
        } catch (error) {
          console.error('Backend submission error:', error)
        };
      }
    });
  }
}

async function addAppointment() {
  if (!appointmentForm.value.name || !appointmentForm.value.email || !appointmentForm.value.service || !appointmentForm.value.date) {
    Swal.fire('Error', 'Please fill in all fields.', 'error')
    return
  }

  const { error } = await supabase.from('appointments').insert({
    client_name: appointmentForm.value.name,
    client_email: appointmentForm.value.email,
    service: appointmentForm.value.service,
    appointment_date: appointmentForm.value.date,
    barber_id: currentUser.value.id,
    status: 0,
  })

  if (error) {
    console.error('Error adding appointment:', error)
    Swal.fire('Error', 'Failed to add appointment.', 'error')
  } else {
    Swal.fire('Success', 'Appointment added successfully.', 'success')
    appointmentForm.value = { name: '', email: '', service: '', date: '' }
  }
}
</script>

<template>
  <div class="row g-4">
    <div class="col-md-6">
      <div class="bh-card p-4">
        <h5 class="brand-font fw-semibold mb-3">Add Walk-In</h5>
        <form @submit.prevent="addWalkIn">
          <div class="mb-3">
            <label class="form-label small fw-semibold">Client Name</label>
            <input type="text" class="form-control bh-input" placeholder="Enter client name" required v-model="walkInForm.name">
          </div>
          <div class="mb-3">
            <label class="form-label small fw-semibold">Client Email</label>
            <input type="email" class="form-control bh-input" placeholder="Enter client email" required v-model="walkInForm.email">
          </div>
          <div class="mb-3">
            <label class="form-label small fw-semibold">Service</label>
            <input type="text" class="form-control bh-input" placeholder="Enter service" required v-model="walkInForm.service">
          </div>
          <button type="submit" class="btn btn-gold rounded-pill w-100 py-2">Add Walk-In</button>
        </form>
      </div>
    </div>

    <div class="col-md-6">
      <div class="bh-card p-4">
        <h5 class="brand-font fw-semibold mb-3">Add Appointment</h5>
        <form @submit.prevent="addAppointment">
          <div class="mb-3">
            <label class="form-label small fw-semibold">Client Name</label>
            <input type="text" class="form-control bh-input" placeholder="Enter client name" required v-model="appointmentForm.name">
          </div>
          <div class="mb-3">
            <label class="form-label small fw-semibold">Client Email</label>
            <input type="email" class="form-control bh-input" placeholder="Enter client email" required v-model="appointmentForm.email">
          </div>
          <div class="mb-3">
            <label class="form-label small fw-semibold">Service</label>
            <input type="text" class="form-control bh-input" placeholder="Enter service" required v-model="appointmentForm.service">
          </div>
          <div class="mb-4">
            <label class="form-label small fw-semibold">Date</label>
            <input type="date" class="form-control bh-input" required v-model="appointmentForm.date">
          </div>
          <button type="submit" class="btn btn-gold rounded-pill w-100 py-2">Add Appointment</button>
        </form>
      </div>
    </div>
  </div>
</template>

<style scoped>
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
