<script setup>
/*
      [0] Waiting for confirmation
      [1] Confirm
      [2] Checked In
      [3] In-Service
      [4] No Show
      [5] Cancel
*/
import Swal from 'sweetalert2';

const loading = ref(false)
const supabase = useSupabase()
const appointments = ref([]);

async function refresh() {
  loading.value = true
  const { data: { user } } = await supabase.auth.getUser()
  const { data, error } = await supabase.from('appointments').select('*').eq('barber_id', user.id)
  if (error) {
    console.error('Error fetching appointments:', error)
  } else {
    appointments.value = data
  }
  loading.value = false
}    

onMounted(refresh)

function completedButtonClick(appt) {
  Swal.fire({
    title: 'Complete Appointment',
    text: 'Are you sure you want to mark this appointment as completed?',
    icon: 'info',
    showCancelButton: false,
    confirmButtonText: 'Yes, mark as completed',
    cancelButtonText: 'Cancel',
  }).then(async (result) => {
    if (result.isConfirmed) {
      const { error } = await supabase.from('clients').update({ appointment_status: 5}).eq('id', appt.id);
      if (error) {
        console.error('Error updating appointment status:', error);
      } else {
        Swal.fire('Completed', 'The appointment has been marked as completed.', 'success');
        await refresh()
      }
    }else {
      Swal.fire('Cancelled', 'The appointment was not marked as completed.', 'info');
    }
  });

}

function cancelAppointment(appt){
  Swal.fire({
    title: 'Cancel Appointmeny',
    text: 'Are you sure you want to cancel this appointment?',
    icon: 'info',
    showCancelButton: true,
    confirmButtonText: 'Yes, cancel appointment',
    cancelButtonText: 'No',
  }).then(async (result) => {
    if (result.isConfirmed) {
      const { error } = await supabase.from('clients').update({ appointment_status: 4}).eq('id', appt.id);
      if (error) {
        console.error('Error updating appointment status:', error);
      } else {
        Swal.fire('Completed', 'The appointment has been marked as completed.', 'success');
        await refresh()
      }
    }else {
      Swal.fire('Cancelled', 'The appointment was not marked as completed.', 'info');
    }
  });
}

async function openAppointmentCreateBox() {
  const { value: formValues } = await Swal.fire({
    title: 'Schedule An Appointment',
    html:
      '<input id="swal-client-name" class="swal2-input" placeholder="Client name">' +
      '<input id="swal-client-email" type="email" class="swal2-input" placeholder="Client email">' +
      '<input id="swal-service" class="swal2-input" placeholder="Service">' +
      '<input id="swal-date" type="date" class="swal2-input">',
    focusConfirm: false,
    showCancelButton: true,
    confirmButtonText: 'Schedule',
    preConfirm: () => {
      const client_name = document.getElementById('swal-client-name').value.trim()
      const client_email = document.getElementById('swal-client-email').value.trim()
      const service = document.getElementById('swal-service').value.trim()
      const appointment_date = document.getElementById('swal-date').value

      if (!client_name || !client_email || !service || !appointment_date) {
        Swal.showValidationMessage('Please fill in all fields')
        return false
      }

      return { client_name, client_email, service, appointment_date }
    },
  })

  if (!formValues) return

  const { data: { user } } = await supabase.auth.getUser()

  const { error } = await supabase.from('clients').insert({
    barber_id: user.id,
    client_name: formValues.client_name,
    client_email: formValues.client_email,
    service: formValues.service,
    appointment_date: formValues.appointment_date,
    appointment_status: 0,
  })

  if (error) {
    Swal.fire('Error', 'Failed to schedule the appointment: ' + error.message, 'error')
  } else {
    Swal.fire('Scheduled', 'The appointment has been created.', 'success')
    await refresh()
  }
}

</script>

<template>
  <div>
    <div class="d-flex flex-wrap align-items-center justify-content-between gap-2 mb-4">
      <div>
        <h1 class="brand-font h3 fw-semibold mb-1">All Scheduled Appointments</h1>
        <p class="text-muted small mb-0">{{ appointments.length }} appointments on the books</p>
      </div>
      <div class="d-flex align-items-center gap-2">

        <button
          type="button"
          class="btn-icon d-flex align-items-center justify-content-center"
          aria-label="Refresh"
          :disabled="loading"
          @click="refresh"
        >
          <svg
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
            width="18"
            height="18"
            :class="{ 'spin': loading }"
          >
            <polyline points="23 4 23 10 17 10" />
            <polyline points="1 20 1 14 7 14" />
            <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15" />
          </svg>
        </button>
      </div>
    </div>

    <div class="bh-card p-4">
      <p><input type="date" class="form-control" placeholder="Search appointments..." /></p>
      <div v-if="loading" class="text-center text-muted py-5">
        Loading appointments…
      </div>

      <div v-else-if="appointments.length === 0" class="text-center text-muted py-5">
        No appointments scheduled.
      </div>

      <div v-else class="table-responsive appointments-table-wrap">
        <table class="table bh-table align-middle mb-0">
          <thead>
            <tr>
              <th scope="col">Client</th>
              <th scope="col">Service</th>
              <th scope="col">Date</th>
              <th scope="col">Status</th>
              <th scope="col" class="text-end"></th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="appt in appointments" :key="appt.id">
              <td>
                <div class="d-flex align-items-center gap-2">
                  
                  <span class="fw-medium">{{ appt.client_name }}</span>
                </div>
              </td>
              <td>{{ appt.service }}</td>
              <td>{{ appt.appointment_date }}</td>
              <td>
                <span class="badge-status" v-if="appt.status === 0">Waiting for confirmation</span>
                <span class="badge-status" v-else-if="appt.status === 1">Confirmed</span>
                <span class="badge-status" v-else-if="appt.status === 2">Checked In</span>
                <span class="badge-status" v-else-if="appt.status === 3">In Service</span>
                <span class="badge-status" v-else-if="appt.status === 4">No Show</span>
                <span class="badge-status" v-else>Canceled</span>
              </td>
              <td class="text-end">
                <button
                  v-if="appt.status==1"
                  type="button"
                  class="btn btn-sm btn-outline-success rounded-pill me-2"
                  @click="completedButtonClick(appt)"
                >
                  Notify
                </button>

                <button
                  type="button"
                  class="btn btn-sm btn-outline-danger rounded-pill"
                  @click="cancelAppointment(appt)"
                >
                  Cancel
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>


<style scoped>
.appointments-table-wrap {
  max-height: 480px;
  overflow-y: auto;
}

.appointments-table-wrap thead th {
  position: sticky;
  top: 0;
  background-color: #fff;
  z-index: 1;
}

.spin {
  animation: spin 0.6s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
</style>
