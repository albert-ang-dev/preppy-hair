import { createClient } from '@supabase/supabase-js';
export default defineNuxtRouteMiddleware(async (to) => {
  const config = useRuntimeConfig()
  const supabase = createClient(config.public.supabaseUrl, config.public.supabaseKey)
  const { data: { session } } = await supabase.auth.getSession()

  const isPublicPath = to.path === '/login' || to.path.startsWith('/book')

  if (!session && !isPublicPath) {
    return navigateTo('/login')
  }
  if (session && to.path === '/login') {
    return navigateTo('/')
  }
})