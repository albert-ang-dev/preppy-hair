<script setup>
const supabase = useSupabase();
const config = useRuntimeConfig();

definePageMeta({ layout: 'blank' });

const view = ref('login'); // 'login' | 'register'

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
            navigateTo('/', { replace: true });
        }
    }).finally(() => {
        loading.value = false;
    });
}

// --- Registration + PayPal subscription ---

const registerForm = ref({ name: '', email: '', password: '' });
const registerError = ref('');
const registerSuccess = ref(false);
const paypalReady = ref(false);

function showRegister() {
    view.value = 'register';
    registerError.value = '';
    loadPaypalSdk();
}

function loadPaypalSdk() {
    if (window.paypal) {
        renderPaypalButton();
        return;
    }

    const script = document.createElement('script');
    script.src = `https://www.paypal.com/sdk/js?client-id=${config.public.paypalClientId}&vault=true&intent=subscription`;
    script.onload = () => renderPaypalButton();
    document.head.appendChild(script);
}

function renderPaypalButton() {
    nextTick(() => {
        paypalReady.value = true;
        window.paypal.Buttons({
            style: { shape: 'pill', color: 'gold', layout: 'vertical', label: 'subscribe' },
            onClick: (data, actions) => {
                registerError.value = '';
                if (!registerForm.value.name || !registerForm.value.email || !registerForm.value.password) {
                    registerError.value = 'Please fill in your name, email, and password first.';
                    return actions.reject();
                }
                return actions.resolve();
            },
            createSubscription: (data, actions) => {
                return actions.subscription.create({
                    plan_id: config.public.paypalPlanId
                });
            },
            onApprove: async (data) => {
                registerError.value = '';

                try {
                    const verifyResponse = await $fetch('/api/payment', {
                        method: 'POST',
                        body: { notify_type: 'paypal-pay', subscription_id: data.subscriptionID }
                    });

                    if (!verifyResponse.success) {
                        registerError.value = 'We could not verify your subscription. Please try again.';
                        return;
                    }
                } catch (err) {
                    console.error('Subscription verification error:', err);
                    registerError.value = 'We could not verify your subscription. Please try again.';
                    return;
                }

                const { data: signUpData, error } = await supabase.auth.signUp({
                    email: registerForm.value.email,
                    password: registerForm.value.password,
                    options: {
                        emailRedirectTo: window.location.origin,
                        data: {
                            display_name: registerForm.value.name,
                            paypal_subscription_id: data.subscriptionID
                        }
                    }
                });

                if (error) {
                    registerError.value = error.message;
                    return;
                }

                try {
                    await $fetch('/api/payment', {
                        method: 'POST',
                        body: {
                            notify_type: 'register-barber',
                            barber_id: signUpData.user.id,
                            barber_name: registerForm.value.name
                        }
                    });
                } catch (err) {
                    console.error('Barber record creation error:', err);
                }

                registerSuccess.value = true;
            },
            onError: (err) => {
                console.error('PayPal error:', err);
                registerError.value = 'Something went wrong with PayPal. Please try again.';
            }
        }).render('#paypal-button-container');
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
                <h1 class="brand-font fs-3 fw-semibold mb-0">{{ view === 'login' ? 'Welcome back' : 'Create your account' }}</h1>
                <p class="text-muted small mb-0">
                    {{ view === 'login' ? 'Sign in to manage your schedule' : '$18/month — cancel anytime' }}
                </p>
            </div>

            <form v-if="view === 'login'" @submit.prevent="login">
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

                <button type="button" class="btn btn-link btn-sm text-muted w-100 mt-2" @click="showRegister">
                    Don't have an account? Register
                </button>
            </form>

            <div v-else>
                <template v-if="!registerSuccess">
                    <div class="mb-3">
                        <label class="form-label small fw-semibold">Name</label>
                        <input type="text" class="form-control bh-input" v-model="registerForm.name" autocomplete="name">
                    </div>
                    <div class="mb-3">
                        <label class="form-label small fw-semibold">Email</label>
                        <input type="email" class="form-control bh-input" v-model="registerForm.email" autocomplete="email">
                    </div>
                    <div class="mb-4">
                        <label class="form-label small fw-semibold">Password</label>
                        <input type="password" class="form-control bh-input" v-model="registerForm.password" autocomplete="new-password">
                    </div>

                    <div v-if="registerError" class="login-error small mb-3">
                        {{ registerError }}
                    </div>

                    <p class="small text-muted mb-2">Complete your $18/month subscription to finish creating your account:</p>
                    <div id="paypal-button-container"></div>
                    <div v-if="!paypalReady" class="text-muted small text-center py-2">Loading payment options…</div>

                    <button type="button" class="btn btn-link btn-sm text-muted w-100 mt-3" @click="view = 'login'">
                        &larr; Back to sign in
                    </button>
                </template>

                <template v-else>
                    <p class="text-muted mb-0">You're subscribed! Check your email to confirm your account, then sign in.</p>
                    <button type="button" class="btn btn-gold rounded-pill w-100 py-2 mt-3" @click="view = 'login'">
                        Go to sign in
                    </button>
                </template>
            </div>
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