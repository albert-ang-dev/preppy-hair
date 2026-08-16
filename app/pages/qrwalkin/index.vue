<script setup>

const route = useRoute();
const supabase = useSupabase()
const checkin_result = ref("");
const needCheckin = ref(true);
const checkedIn = ref({ name: '', service: '', id: null });


definePageMeta({ layout: 'blank' });

const form = ref({
  name: '',
  email: '',
  service: ''
});
const barber = route.query.barberid;
const barberName = ref("");

onMounted(async () =>{
    await supabase.from("preppyhair_barbers").select("*").eq("barber_id",barber).then(async({ data, error }) => {
        if(error == null){
            barberName.value = data[0].barber_name;
        }
    });


})

async function submitCheckIn() {
  // TODO: wire up backend submission
  await supabase.from("walkins").insert({
    client_name:form.value.name,
    client_email:form.value.email,
    service: form.value.service,
    barber_id: barber,
    status:2
  }).select().then(async({ data, error }) => {
    if(error){
        checkin_result.value = "Something went wrong, try again";
    }else{
      checkin_result.value = "You are now checked in!";
      checkedIn.value = { name: form.value.name, service: form.value.service, id: data[0].id };
      needCheckin.value = false;
    }

    form.value = {name:"",email:"",service:""}
  });
}
</script>

<template>
  <div class="checkin-page d-flex align-items-center justify-content-center">
    <div class="bh-card p-5 checkin-card" v-if="needCheckin">
      <div class="d-flex flex-column align-items-center text-center mb-4">
        <div class="sidebar-mark d-flex align-items-center justify-content-center mb-3">
          <i class="bi bi-scissors"></i>
        </div>
        <div class="topbar-eyebrow text-uppercase fw-semibold">Preppy Hair Studio</div>
        <h1 class="brand-font fs-3 fw-semibold mb-0">Check In</h1>
        <p class="text-muted small mb-0">Enter your info to join the walk-in queue</p>
      </div>

      <form @submit.prevent="submitCheckIn">
        <h4>{{ barberName }}</h4>
        <div class="mb-3">
          <label class="form-label small fw-semibold">Name</label>
          <input type="text" class="form-control bh-input" placeholder="Enter your name" required v-model="form.name">
        </div>
        <div class="mb-3">
          <label class="form-label small fw-semibold">Email</label>
          <input type="email" class="form-control bh-input" placeholder="Enter your email" required v-model="form.email">
        </div>
        <div class="mb-4">
          <label class="form-label small fw-semibold">Service</label>
          <input type="text" class="form-control bh-input" placeholder="Enter service" required v-model="form.service">
        </div>
        <button type="submit" class="btn btn-gold rounded-pill w-100 py-2">Check In</button>
      </form>
    </div>

    <div class="bh-card p-5 checkin-card text-center" v-else>
      <div class="checkin-success-mark d-flex align-items-center justify-content-center mb-3 mx-auto">
        <i class="bi bi-check-lg"></i>
      </div>
      <div class="topbar-eyebrow text-uppercase fw-semibold">Preppy Hair Studio</div>
      <h1 class="brand-font fs-3 fw-semibold mb-2">{{ checkin_result }}</h1>
      <p class="text-muted small mb-4">We'll let you know when it's almost your turn.</p>

      <div class="checkin-summary text-start mb-4">
        <div class="d-flex justify-content-between py-2">
          <span class="text-muted small">Barber</span>
          <span class="fw-semibold small">{{ barberName }}</span>
        </div>
        <div class="d-flex justify-content-between py-2">
          <span class="text-muted small">Name</span>
          <span class="fw-semibold small">{{ checkedIn.name }}</span>
        </div>
        <div class="d-flex justify-content-between py-2">
          <span class="text-muted small">Service</span>
          <span class="fw-semibold small">{{ checkedIn.service }}</span>
        </div>
      </div>

      <NuxtLink
        v-if="checkedIn.id"
        :to="`/waitlist/${barber}?appointment_id=${checkedIn.id}`"
        class="btn btn-gold rounded-pill w-100 py-2"
      >
        View my position in line
      </NuxtLink>
    </div>
  </div>
</template>

<style scoped>
.checkin-page {
  min-height: 100vh;
  background-color: var(--bh-bg);
  padding: 1.5rem;
}

.checkin-card {
  width: 100%;
  max-width: 400px;
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

.checkin-success-mark {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--bh-gold), var(--bh-gold-dark));
  color: #ffffff;
  font-size: 26px;
  box-shadow: 0 4px 14px rgba(199, 160, 89, 0.35);
}

.checkin-summary {
  background: var(--bh-bg);
  border: 1px solid var(--bh-border);
  border-radius: 12px;
  padding: 0.25rem 1rem;
}

.checkin-summary > div:not(:last-child) {
  border-bottom: 1px solid var(--bh-border);
}
</style>
