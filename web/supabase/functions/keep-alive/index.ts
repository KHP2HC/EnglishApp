// Supabase Edge Function: Keep-Alive (prevents free-tier auto-pause)
// Schedule via Supabase Dashboard → Edge Functions → Cron: 0 9 */5 * *

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
}

Deno.serve(async () => {
  const supabaseUrl = Deno.env.get('SUPABASE_URL')
  const supabaseKey = Deno.env.get('SUPABASE_ANON_KEY')

  if (supabaseUrl && supabaseKey) {
    try {
      await fetch(`${supabaseUrl}/rest/v1/profiles?select=id&limit=1`, {
        headers: {
          apikey: supabaseKey,
          Authorization: `Bearer ${supabaseKey}`,
        },
      })
    } catch {
      // ignore — the request itself keeps the project warm
    }
  }

  return new Response(
    JSON.stringify({ status: 'alive', timestamp: new Date().toISOString() }),
    { headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
  )
})
