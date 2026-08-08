export default defineNuxtRouteMiddleware(async (to) => {
  const supabase = useSupabase()
  const { data: { session } } = await supabase.auth.getSession()

  const isPublicPath = to.path === '/login' || to.path.startsWith('/book') || to.path.startsWith('/waitlist')

  if (!session && !isPublicPath) {
    return navigateTo('/login')
  }
  if (session && to.path === '/login') {
    return navigateTo('/')
  }
})