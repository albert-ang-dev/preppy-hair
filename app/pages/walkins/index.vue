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
    <h3>WalkIns</h3>

    <div class="row">
      <div class="col-md-5">
        <p>Client name <input type="text" class="form-control"></p>
        <p>Service <input type="text" class="form-control"></p>
        <p>Client Email <input type="email" class="form-control"></p>
        <p><button class="btn btn-primary">Add Walk-in</button></p>
      </div>

      <div class="col-md-7">
        <!-- This is where the walk-in clients tabs will be displayed -->
        <div class="walkins-list-wrap pe-2">
          <div
            v-for="walkIn in walkIns"
            :key="walkIn.id"
            class="card bh-card border-0 mb-3"
          >
            <div class="card-body d-flex align-items-center gap-3">
              <div class="avatar-initial d-flex align-items-center justify-content-center">
                {{ initials(walkIn.name) }}
              </div>

              <div class="flex-grow-1">
                <h5 class="card-title brand-font fw-semibold mb-1">{{ walkIn.name }}</h5>
                <p class="card-text small text-muted mb-1">Walk in Client ID: #{{ walkIn.clientId }}</p>
                <span class="badge-status status-waitlist">Waitlist #{{ walkIn.waitlist }}</span>
              </div>

              <button type="button" class="btn-icon d-flex align-items-center justify-content-center" aria-label="Select client" @click="openOptionBox(walkIn)">
                <i class="bi bi-arrow-return-left fs-5"></i>
              </button>
            </div>
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
