<template>
  <div class="d-flex">
    <aside class="sidebar d-none d-md-flex flex-column align-items-center py-4 gap-3">
      <div class="sidebar-mark d-flex align-items-center justify-content-center">
        <i class="bi bi-scissors"></i>
      </div>

      <div class="sidebar-divider my-1"></div>

      <NuxtLink
        to="/"
        class="sidebar-link d-flex align-items-center justify-content-center"
        :class="{ active: route.path === '/' }"
        aria-label="Home"
        title="Home"
      >
        <i class="bi bi-house"></i>
      </NuxtLink>

      <NuxtLink
        to="/appointments"
        class="sidebar-link d-flex align-items-center justify-content-center"
        :class="{ active: route.path.startsWith('/appointments') }"
        aria-label="Appointments"
        title="Appointments"
      >
        <i class="bi bi-calendar3"></i>
      </NuxtLink>

      <NuxtLink
        to="/walkins"
        class="sidebar-link d-flex align-items-center justify-content-center"
        :class="{ active: route.path.startsWith('/walkins') }"
        aria-label="Walk-ins"
        title="Walk-ins"
      >
        <i class="bi bi-people"></i>
      </NuxtLink>

      <button
        type="button"
        class="sidebar-link d-flex align-items-center justify-content-center border-0 bg-transparent mt-auto"
        aria-label="Log out"
        title="Log out"
        @click="logout"
      >
        <i class="bi bi-box-arrow-right"></i>
      </button>
    </aside>

    <div class="content-col flex-grow-1 d-flex flex-column">
      <header class="topbar d-flex align-items-center justify-content-between px-4 py-3 bg-white">
        <div>
          <div class="topbar-eyebrow text-uppercase fw-semibold">Preppy Hair Studio</div>
          <div class="brand-font fs-5 fw-semibold">Barbershop &amp; Salon</div>
        </div>
        <div class="text-muted small text-end d-none d-sm-block">{{ today }}</div>
      </header>

      <main class="flex-grow-1 p-4">
        <slot />
      </main>
    </div>

    <div class="mobile-fab-wrap d-md-none">
      <div v-if="mobileMenuOpen" class="mobile-fab-menu bh-card p-2">
        <NuxtLink to="/" class="mobile-fab-link d-flex align-items-center gap-2" @click="mobileMenuOpen = false">
          <i class="bi bi-house"></i> Home
        </NuxtLink>
        <NuxtLink to="/appointments" class="mobile-fab-link d-flex align-items-center gap-2" @click="mobileMenuOpen = false">
          <i class="bi bi-calendar3"></i> Appointments
        </NuxtLink>
        <NuxtLink to="/walkins" class="mobile-fab-link d-flex align-items-center gap-2" @click="mobileMenuOpen = false">
          <i class="bi bi-people"></i> Walk-ins
        </NuxtLink>
        <button type="button" class="mobile-fab-link d-flex align-items-center gap-2 border-0 bg-transparent w-100 text-start" @click="logout">
          <i class="bi bi-box-arrow-right"></i> Log out
        </button>
      </div>

      <button
        type="button"
        class="mobile-fab d-flex align-items-center justify-content-center"
        aria-label="Toggle menu"
        @click="mobileMenuOpen = !mobileMenuOpen"
      >
        <i :class="mobileMenuOpen ? 'bi bi-x-lg' : 'bi bi-list'"></i>
      </button>
    </div>
  </div>
</template>

<script setup>
const supabase = useSupabase();

const route = useRoute()
const mobileMenuOpen = ref(false)

const today = new Date().toLocaleDateString(undefined, {
  weekday: 'long',
  month: 'long',
  day: 'numeric'
})

function logout() {
  mobileMenuOpen.value = false
  supabase.auth.signOut().then(() => {
    navigateTo('/login');
  }).catch((error) => {
    console.error('Error signing out:', error);
  });
}
</script>
