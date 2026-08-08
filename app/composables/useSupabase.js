import { createClient } from '@supabase/supabase-js'

let supabaseClient = null

export function useSupabase() {
  const config = useRuntimeConfig()

  if (import.meta.server) {
    return createClient(config.public.supabaseUrl, config.public.supabaseKey)
  }

  if (!supabaseClient) {
    supabaseClient = createClient(config.public.supabaseUrl, config.public.supabaseKey)
  }

  return supabaseClient
}
