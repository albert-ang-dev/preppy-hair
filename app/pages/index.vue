<script setup>
import Swal from 'sweetalert2';

const supabase = useSupabase();

const loading = ref(false)
const saving = ref(false)
const saveMessage = ref('')
const currentUser = ref(null)
const barberLink = ref("");

onMounted(async () => {
  const { data: { user } } = await supabase.auth.getUser()
  currentUser.value = user;
  barberLink.value = "http://api.qrserver.com/v1/create-qr-code/?data=https://preppyhair.site/qrwalkin?barberid="+currentUser.value.id + "&size=200x200";
});

function deleteAccountClicked() {
  Swal.fire({
    title: 'Delete your account?',
    text: 'This will sign you out and cannot be undone.',
    icon: 'warning',
    showCancelButton: true,
    confirmButtonText: 'Yes, delete my account',
    cancelButtonText: 'Cancel',
    confirmButtonColor: '#d33',
  }).then(async (result) => {
    if (result.isConfirmed) {
      // NOTE: fully deleting the auth user requires a backend endpoint using
      // the Supabase service role key (not safe to expose client-side).
      // This currently only signs the user out.
      await supabase.auth.signOut()
      navigateTo('/login', { replace: true })
    }
  });
}
</script>

<template>
  <div class="bh-card p-5">
    <div class="topbar-eyebrow text-uppercase fw-semibold mb-2">Welcome back</div>
    <h1 class="brand-font display-6 fw-semibold mb-3">Ready for today's clients?</h1>
    <p class="text-muted mb-4" style="max-width: 32rem;">
      Use the sidebar to review today's schedule, check in appointments, and keep the chairs full.
    </p>

    <div v-if="currentUser" class="row g-4">
      <div class="col-md-6">
        <h5 class="brand-font fw-semibold mb-3">Account Information</h5>
        <div class="account-info">
          <div class="mb-2">
            <span class="text-muted small">User ID</span>
            <p class="mb-0 fw-medium">{{ currentUser.id }}</p>
          </div>
          <div class="mb-2">
            <span class="text-muted small">Display Name</span>
            <p class="mb-0 fw-medium">{{ currentUser.user_metadata?.display_name || 'Not set' }} <button class="btn btn-warning"><i class="bi bi-pencil"></i></button></p>
          </div>
          <div class="mb-0">
            <span class="text-muted small">Phone Number</span>
            <p class="mb-0 fw-medium">{{ currentUser.phone || 'Not set' }}</p>
          </div>
        </div>
      </div>

      <div class="col-md-6">
        <h5 class="brand-font fw-semibold mb-3">Your QR Code</h5>
        <img :src="barberLink" alt="Your check-in QR code" class="mb-4">
        <div>
          <button type="button" class="btn btn-outline-danger rounded-pill" @click="deleteAccountClicked">
            Delete Account
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.availability-day-label {
  width: 100px;
}
</style>
