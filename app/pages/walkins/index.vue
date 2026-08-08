<script setup>
import Swal from 'sweetalert2';
import { createClient } from '@supabase/supabase-js';

const config = useRuntimeConfig();
const supabase = createClient(config.public.supabaseUrl, config.public.supabaseKey);
const walkIns = ref([]);
const currentUser = ref(null);
const walkInForm = ref({
  name: '',
  email: '',
  service: ''
});


onMounted(async () => {
  const { data: { user } } = await supabase.auth.getUser()
  currentUser.value = user;
  getWalkIns();
})


function initials(name) {
  return name
    .split(' ')
    .map((part) => part[0])
    .join('')
    .slice(0, 2)
    .toUpperCase()
}

function getWalkIns(){
  supabase.from('walkins').select('*').eq('barber_id', currentUser.value.id).then(({ data, error }) => {
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
              client_appt_id: data[0].id // Replace with the actual client appointment ID
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
      const { error } = await supabase.from('walkins').delete().eq('id', walkins.id);
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
            // Reset form on success
            walkInForm.value = { name: '', email: '', service: '' };
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
      const { error } = await supabase.from('walkins').update({ appointment_status: 2}).eq('id', walkins.id);
      if (error) {
        console.error('Error updating appointment status:', error);
      } else {
        Swal.fire('In Service', 'The appointment has been marked as in service.', 'success');

         try {
          // Vercel routes '/api/send' directly to your 'api/send.py' script
          const response = await $fetch('/api/notify', {
            method: 'POST',
            body: {
              notify_type: 'walkin-in-service',
              email: walkins.client_email,
              name: walkins.client_name,}
          })

          if (response.success) {
            Swal.fire('Success', 'Notification email sent successfully.', 'success');
            // Reset form on success
            walkInForm.value = { name: '', email: '', service: '' };
          }
        } catch (error) {
          console.error('Backend submission error:', error)
        };               
        getWalkIns(); // Refresh the walk-ins list
      }
    }else {
      Swal.fire('Cancelled', 'The appointment was not marked as in service.', 'info');
    }
  });
}
</script>

<template>
  <div class="container-fluid">
    <h3>Ques</h3>

    <div class="row">
      <div class="col-md-4 ">
        <h5>Add Walk-Ins</h5>
        <br>
        <p>Client Name <input type="text" class="form-control" placeholder="Enter client name" required v-model="walkInForm.name"></p>
        <p>Client Email  <input type="email" class="form-control" placeholder="Enter client email" required v-model="walkInForm.email"></p>
        <p>Service  <input type="text" class="form-control" placeholder="Enter service" required v-model="walkInForm.service"></p>
        <p><button class="btn btn-primary" @click="addWalkIn">Add Walk-In</button></p>
      </div>

      <div class="col-md-4 ">
        <h5>Walkins</h5>

        <div class="overflow-auto walkins-list-wrap">
          <div class="card p-3 m-2" v-for="n in walkIns" :key="n.id" >
            <p>{{ n.client_name }}</p>
            <p>{{ n.service }}</p>
            <p>{{ n.created_at }}</p>
            <p><button class="btn btn-info btn-sm" @click="inServiceClicked(n)">In Service</button> <button class="btn btn-danger btn-sm" @click="noShowClicked(n)">No Show</button></p>
          </div>
        </div>
      </div>
     

      <div class="col-md-4">
        <h5>Appointment today</h5>
        
        <div class="overflow-auto walkins-list-wrap">
          <div class="card p-3 m-2" v-for="n in 20">
            <p>Hello WOrld</p>
          </div>
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
</style>
