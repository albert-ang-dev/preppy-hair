<!-- <script setup>
import { ref } from 'vue'

// Form state variables
const form = ref({
  name: '',
  email: '',
  message: ''
})

const isSubmitting = ref(false)
const statusMessage = ref('')

const handleSubmit = async () => {
  isSubmitting.value = true
  statusMessage.value = ''

  try {
    // Vercel routes '/api/send' directly to your 'api/send.py' script
    const response = await $fetch('/api/send', {
      method: 'POST',
      body: form.value
    })

    if (response.success) {
      statusMessage.value = 'Success! Your message was sent.'
      // Reset form on success
      form.value = { name: '', email: '', message: '' }
    }
  } catch (error) {
    statusMessage.value = 'Error sending message. Please try again.'
    console.error('Backend submission error:', error)
  } finally {
    isSubmitting.value = false
  }
}
</script> -->



<script setup>
import { createClient } from '@supabase/supabase-js';

const config = useRuntimeConfig();
const supabase = createClient(config.public.supabaseUrl, config.public.supabaseKey);

definePageMeta({ layout: 'blank' });

const email = ref('');
const password = ref('');
const errorMsg = ref('');
const loading = ref(false);

function login() {
    errorMsg.value = '';
    loading.value = true;
    supabase.auth.signInWithPassword({
        email: email.value,
        password: password.value
    }).then(({ error }) => {
        if (error) {
            errorMsg.value = error.message;
        } else {
            navigateTo('/');
        }
    }).finally(() => {
        loading.value = false;
    });
}
</script>



<template>
    <div class="login-page d-flex align-items-center justify-content-center">
        <div class="bh-card p-5 login-card">
            <div class="d-flex flex-column align-items-center text-center mb-4">
                <div class="sidebar-mark d-flex align-items-center justify-content-center mb-3">
                    <i class="bi bi-scissors"></i>
                </div>
                <div class="topbar-eyebrow text-uppercase fw-semibold">Preppy Hair Studio</div>
                <h1 class="brand-font fs-3 fw-semibold mb-0">Welcome back</h1>
                <p class="text-muted small mb-0">Sign in to manage your schedule</p>
            </div>

            <form @submit.prevent="login">
                <div class="mb-3">
                    <label for="email" class="form-label small fw-semibold">Email</label>
                    <input
                        id="email"
                        type="email"
                        class="form-control bh-input"
                        v-model="email"
                        autocomplete="email"
                        required
                    >
                </div>
                <div class="mb-4">
                    <label for="password" class="form-label small fw-semibold">Password</label>
                    <input
                        id="password"
                        type="password"
                        class="form-control bh-input"
                        v-model="password"
                        autocomplete="current-password"
                        required
                    >
                </div>

                <div v-if="errorMsg" class="login-error small mb-3">
                    {{ errorMsg }}
                </div>

                <button type="submit" class="btn btn-gold rounded-pill w-100 py-2" :disabled="loading">
                    {{ loading ? 'Signing in…' : 'Sign in' }}
                </button>
            </form>
        </div>
    </div>
</template>

<style scoped>
.login-page {
    min-height: 100vh;
    background-color: var(--bh-bg);
    padding: 1.5rem;
}

.login-card {
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

.login-error {
    background: #fdeceb;
    color: #d84c3f;
    border-radius: 10px;
    padding: 0.6rem 0.85rem;
}
</style>