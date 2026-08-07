<script setup>
import Swal from 'sweetalert2';
const walkIns = ref([
  { id: 1, name: 'Albert Ang', clientId: '15153', waitlist: 1 },
  { id: 2, name: 'Maria Santos', clientId: '15154', waitlist: 2 },
  { id: 3, name: 'James Cruz', clientId: '15155', waitlist: 3 },
  { id: 4, name: 'Liza Reyes', clientId: '15156', waitlist: 4 },
  { id: 5, name: 'Noah Bautista', clientId: '15157', waitlist: 5 },
    { id: 1, name: 'Albert Ang', clientId: '15153', waitlist: 1 },
  { id: 2, name: 'Maria Santos', clientId: '15154', waitlist: 2 },
  { id: 3, name: 'James Cruz', clientId: '15155', waitlist: 3 },
  { id: 4, name: 'Liza Reyes', clientId: '15156', waitlist: 4 },
  { id: 5, name: 'Noah Bautista', clientId: '15157', waitlist: 5 },
    { id: 1, name: 'Albert Ang', clientId: '15153', waitlist: 1 },
  { id: 2, name: 'Maria Santos', clientId: '15154', waitlist: 2 },
  { id: 3, name: 'James Cruz', clientId: '15155', waitlist: 3 },
  { id: 4, name: 'Liza Reyes', clientId: '15156', waitlist: 4 },
  { id: 5, name: 'Noah Bautista', clientId: '15157', waitlist: 5 },
])

function initials(name) {
  return name
    .split(' ')
    .map((part) => part[0])
    .join('')
    .slice(0, 2)
    .toUpperCase()
}

function openOptionBox(walkIn) {
  Swal.fire('Option Selected', 'You have selected a walk-in client. ' + walkIn.name, 'info');
}
</script>

<template>
  <div class="container-fluid">
    <h3>Ques</h3>

    <div class="row">
      <div class="col-md-4 ">
        <h5>Add Walk-Ins</h5>
        <br>
        <p>Client Name <input type="text" class="form-control" placeholder="Enter client name" required></p>
        <p>Client Email  <input type="email" class="form-control" placeholder="Enter client email" required></p>
        <p>Service  <input type="text" class="form-control" placeholder="Enter service" required></p>
        <p><button class="btn btn-primary">Add Walk-In</button></p>
      </div>

      <div class="col-md-4 ">
        <h5>Walkins</h5>

        <div class="overflow-auto walkins-list-wrap">
          <div class="card p-3 m-2" v-for="n in 20">
            <p>Hello WOrld</p>
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
