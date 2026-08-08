<script setup>
import { createClient } from '@supabase/supabase-js';

const config = useRuntimeConfig();
const supabase = createClient(config.public.supabaseUrl, config.public.supabaseKey);

const loading = ref(false)
const saving = ref(false)
const saveMessage = ref('')

onMounted(async () => {
  const { data: { user } } = await supabase.auth.getUser()
  
});
</script>

<template>
  <div class="bh-card p-5">
    <div class="topbar-eyebrow text-uppercase fw-semibold mb-2">Welcome back</div>
    <h1 class="brand-font display-6 fw-semibold mb-3">Ready for today's clients?</h1>
    <p class="text-muted mb-4" style="max-width: 32rem;">
      Use the sidebar to review today's schedule, check in appointments, and keep the chairs full.
    </p>


  </div>
</template>

<style scoped>
.availability-day-label {
  width: 100px;
}
</style>
