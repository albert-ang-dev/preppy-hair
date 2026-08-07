<script setup>
import Swal from 'sweetalert2';
import { createClient } from '@supabase/supabase-js';

const loading = ref(false)
const config = useRuntimeConfig()
const supabase = createClient(config.public.supabaseUrl, config.public.supabaseKey)
const appointments = ref([]);
onMounted(async () => {
  loading.value = true
  const { data, error } = await supabase.from('clients').select('*').eq('barber_id', (await supabase.auth.getUser()).data.user.id);
  if (error) {
    console.error('Error fetching appointments:', error)
  } else {
    appointments.value = data;
  }
  loading.value = false
})

function completedButtonClick(appt) {
  console.log('Completed button clicked for appointment:', appt);
  Swal.fire({
    title: 'Complete Appointment',
    text: 'Are you sure you want to mark this appointment as completed?',
    icon: 'info',
    showCancelButton: false,
    confirmButtonText: 'Yes, mark as completed',
    cancelButtonText: 'Cancel',
  }).then(async (result) => {
    if (result.isConfirmed) {
      const { error } = await supabase.from('clients').update({ appointment_status: 1}).eq('id', appt.id);
      if (error) {
        console.error('Error updating appointment status:', error);
      } else {
        Swal.fire('Completed', 'The appointment has been marked as completed.', 'success');
        // Refresh the appointments list
        const { data, error } = await supabase.from('clients').select('*');
        if (error) {
          console.error('Error fetching appointments:', error);
        } else {
          appointments.value = data;
        }
      }
    }else {
      Swal.fire('Cancelled', 'The appointment was not marked as completed.', 'info');
    }
  });

}

function noShowButtonClick(appt) {
  console.log('No Show button clicked for appointment:', appt);
  Swal.fire({
    title: 'Mark as No Show',
    text: 'Are you sure you want to mark this appointment as a no show?',
    icon: 'warning',
    showCancelButton: false,
    confirmButtonText: 'Yes, mark as no show',
    cancelButtonText: 'Cancel',
  }).then(async (result) => {
    if (result.isConfirmed) {
      const { error } = await supabase.from('clients').delete().eq('id', appt.id);
      if (error) {
        console.error('Error updating appointment status:', error);
      } else {
        Swal.fire('No Show', 'The appointment has been marked as a no show.', 'success');
        // Refresh the appointments list
        const { data, error } = await supabase.from('clients').select('*');
        if (error) {
          console.error('Error fetching appointments:', error);
        } else {
          appointments.value = data;
        }
      }
    }else {
      Swal.fire('Cancelled', 'The appointment was not marked as a no show.', 'info');
    }
  });
}

</script>

<template>
  <div>
    <div class="d-flex flex-wrap align-items-center justify-content-between gap-2 mb-4">
      <div>
        <h1 class="brand-font h3 fw-semibold mb-1">All Scheduled Appointments</h1>
        <p class="text-muted small mb-0">{{ appointments.length }} appointments on the books</p>
      </div>
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
              <th scope="col">Time</th>
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
              <td>{{ appt.appointment_time }}</td>
              <td>
                <span class="badge-status" v-if="appt.appointment_status === 0">Scheduled</span>
                <span class="badge-status" v-else-if="appt.appointment_status === 1">Completed</span>
                <span class="badge-status" v-else>No Show</span>
              </td>
              <td class="text-end">
                <button
                  type="button"
                  class="btn btn-sm btn-outline-success rounded-pill me-2"
                  @click="completedButtonClick(appt)"
                >
                  Aprove
                </button>

                <button
                  type="button"
                  class="btn btn-sm btn-outline-danger rounded-pill"
                  @click="noShowButtonClick(appt)"
                >
                  Decline
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
