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

const supabase = useSupabase();
const walkIns = ref([]);
const todaysAppointments = ref([]);
const currentUser = ref(null);


onMounted(async () => {
  const { data: { user } } = await supabase.auth.getUser()
  currentUser.value = user;
  getWalkIns();
  getTodaysAppointments();
})

function todayDateKey() {
  const now = new Date()
  const year = now.getFullYear()
  const month = String(now.getMonth() + 1).padStart(2, '0')
  const day = String(now.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

function getTodaysAppointments(){
  supabase
    .from('appointments')
    .select('*')
    .eq('barber_id', currentUser.value.id)
    .eq('appointment_date', todayDateKey())
    .eq('status', 1)
    .then(({ data, error }) => {
      if (error) {
        console.error('Error fetching today\'s appointments:', error);
      } else {
        todaysAppointments.value = data;
      }
    });
}

function appointmentCheckInClicked(appt){
  Swal.fire({
    title: 'Are you sure?',
    text: `Check in ${appt.client_name}?`,
    icon: 'info',
    showCancelButton: true,
    confirmButtonColor: '#3085d6',
    cancelButtonColor: '#d33',
    confirmButtonText: 'Yes, check in!'
  }).then(async (result) => {
    if (result.isConfirmed) {
      const { error } = await supabase.from('appointments').update({ appointment_status: 2 }).eq('id', appt.id);
      if (error) {
        console.error('Error checking in appointment:', error);
      } else {
        Swal.fire('Checked In', `${appt.client_name} has been checked in.`, 'success');
        getTodaysAppointments();
      }
    } else {
      Swal.fire('Cancelled', 'The appointment was not checked in.', 'info');
    }
  });
}

function appointmentNoShowClicked(appt){
  Swal.fire({
    title: 'Are you sure?',
    text: `Mark ${appt.client_name} as a no show?`,
    icon: 'warning',
    showCancelButton: true,
    confirmButtonColor: '#3085d6',
    cancelButtonColor: '#d33',
    confirmButtonText: 'Yes, mark as no show!'
  }).then(async (result) => {
    if (result.isConfirmed) {
      const { error } = await supabase.from('appointments').update({ appointment_status: 4 }).eq('id', appt.id);
      if (error) {
        console.error('Error marking appointment as no show:', error);
      } else {
        Swal.fire('No Show', `${appt.client_name} has been marked as a no show.`, 'success');
        getTodaysAppointments();
      }
    } else {
      Swal.fire('Cancelled', 'The appointment was not marked as a no show.', 'info');
    }
  });
}


function initials(name) {
  return name
    .split(' ')
    .map((part) => part[0])
    .join('')
    .slice(0, 2)
    .toUpperCase()
}

function getWalkIns(){
  supabase.from('walkins').select('*').eq('barber_id', currentUser.value.id).eq('status', 2).then(({ data, error }) => {
    if (error) {
      console.error('Error fetching walk-ins:', error);
    } else {
      walkIns.value = data;
      for(let i=0; i<walkIns.value.length; i++){
        const dbTimestamp = new Date(walkIns.value[i].created_at);
        walkIns.value[i].created_at = dbTimestamp.toLocaleString();
      }
    }
  });
}



function noShowClicked(walkins){
  Swal.fire({
    title: 'Are you sure?',
    text: "You are about to mark this appointment as a no show.",
    icon: 'warning',
    showCancelButton: true,
    confirmButtonColor: '#3085d6',
    cancelButtonColor: '#d33',
    confirmButtonText: 'Yes, mark as no show!'
  }).then(async (result) => {
    if (result.isConfirmed) {
      const { error } = await supabase.from('walkins').update({ status: 4}).eq('id', walkins.id);
      if (error) {
        console.error('Error updating appointment status:', error);
      } else {
        // ALERT THE CLIENT THAT THE APPOINTMENT HAS BEEN MARKED AS A NO SHOW
        Swal.fire('No Show', 'The appointment has been marked as a no show.', 'success');

         try {
          // Vercel routes '/api/send' directly to your 'api/send.py' script
          const response = await $fetch('/api/notify', {
            method: 'POST',
            body: {
              notify_type: 'walkin-no-show',
              email: walkins.client_email,
              name: walkins.client_name,}
          })

          if (response.success) {
            Swal.fire('Success', 'Notification email sent successfully.', 'success');
          }
        } catch (error) {
          console.error('Backend submission error:', error)
        };       
        getWalkIns(); // Refresh the walk-ins list
      }
    }else {
      Swal.fire('Cancelled', 'The appointment was not marked as a no show.', 'info');
    }
  });
}


function inServiceClicked(walkins){
  Swal.fire({
    title: 'Are you sure?',
    text: "You are about to mark this appointment as in service.",
    icon: 'info',
    showCancelButton: true,
    confirmButtonColor: '#3085d6',
    cancelButtonColor: '#d33',
    confirmButtonText: 'Yes, mark as in service!'
  }).then(async (result) => {
    if (result.isConfirmed) {
         const result = await supabase.from('walkins').update({ status: 4}).eq('id', walkins.id);
         if(result.error == null){
            try {
              // Vercel routes '/api/send' directly to your 'api/send.py' script
              const response = await $fetch('/api/notify', {
                method: 'POST',
                body: {
                  notify_type: 'walkin-in-service',
                  email: walkins.client_email,
                  name: walkins.client_name,}
              });

              if (response.success) {
                Swal.fire('Success', 'Notification email sent successfully.', 'success');
              }
            } catch (error) {
              console.error('Backend submission error:', error)
            };
            console.log("GOOD!");
         };
               
        getWalkIns(); // Refresh the walk-ins list
        
    }


  });
}
</script>

<template>
  <div class="container-fluid">

    <div class="row">

      <div class="col-md-6 ">
        <h5 class="brand-font fw-semibold mb-3">Walkins / Checked Ins</h5>

        <div class="overflow-auto walkins-list-wrap">
          <div class="card bh-card border-0 mb-3" v-for="n in walkIns" :key="n.id">
            <div class="card-body d-flex align-items-center gap-3">
              <div class="avatar-initial d-flex align-items-center justify-content-center">
                {{ initials(n.client_name) }}
              </div>

              <div class="flex-grow-1">
                <h6 class="brand-font fw-semibold mb-1">{{ n.client_name }}</h6>
                <p class="small text-muted mb-1">{{ n.service }}</p>
                <p class="small text-muted mb-0">Checked in {{ n.created_at }}</p>
              </div>

              <div class="d-flex flex-column gap-2">
                <button type="button" class="btn btn-sm btn-outline-success rounded-pill" @click="inServiceClicked(n)">In Service</button>
                <button type="button" class="btn btn-sm btn-outline-danger rounded-pill" @click="noShowClicked(n)">No Show</button>
              </div>
            </div>
          </div>

          <p v-if="walkIns.length === 0" class="text-center text-muted py-5 mb-0">No check in yet.</p>
        </div>
      </div>
     
      <div class="col-md-6">
        <h5 class="brand-font fw-semibold mb-3">Appointment today</h5>

        <div class="overflow-auto walkins-list-wrap">
          <div class="card bh-card border-0 mb-3" v-for="appt in todaysAppointments" :key="appt.id">
            <div class="card-body d-flex align-items-center gap-3">
              <div class="avatar-initial d-flex align-items-center justify-content-center">
                {{ initials(appt.client_name) }}
              </div>

              <div class="flex-grow-1">
                <h6 class="brand-font fw-semibold mb-1">{{ appt.client_name }}</h6>
                <p class="small text-muted mb-1">{{ appt.service }}</p>
                <p class="small text-muted mb-0">{{ appt.appointment_time }}</p>
              </div>

              <div class="d-flex flex-column gap-2">
                <button type="button" class="btn btn-sm btn-outline-success rounded-pill" @click="appointmentCheckInClicked(appt)">Check In</button>
                <button type="button" class="btn btn-sm btn-outline-danger rounded-pill" @click="appointmentNoShowClicked(appt)">No Show</button>
              </div>
            </div>
          </div>

          <p v-if="todaysAppointments.length === 0" class="text-center text-muted py-5 mb-0">No appointments today.</p>
        </div>
      </div>
      
    </div>
  </div>
</template>

<style scoped>
.walkins-list-wrap {
  max-height: 600px;
  overflow-y: auto;
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
