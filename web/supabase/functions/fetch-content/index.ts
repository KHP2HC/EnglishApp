// Supabase Edge Function: Content Fetcher (VOA/BBC scraper proxy)
// Deploy: supabase functions deploy fetch-content

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
}

const SOURCES: Record<string, string> = {
  voa: 'https://learningenglish.voanews.com',
  bbc: 'https://www.bbc.co.uk/learningenglish/english/features/6-minute-english',
}

function tagDifficulty(text: string): string {
  const words = text.split(/\s+/).length
  if (words < 200) return 'A2'
  if (words < 400) return 'B1'
  if (words < 800) return 'B2'
  return 'C1'
}

function extractArticles(html: string, source: string) {
  const articles: any[] = []
  // Simple regex-based extraction (Deno has no DOM parser by default)
  const itemRegex = /<(?:article|div)[^>]*class="[^"]*(?:media|item|story|episode)[^"]*"[^>]*>([\s\S]*?)<\/(?:article|div)>/gi
  const titleRegex = /<a[^>]*>([^<]+)<\/a>/i
  const linkRegex = /<a[^>]*href="([^"]+)"[^>]*>/i

  let match
  while ((match = itemRegex.exec(html)) !== null && articles.length < 10) {
    const block = match[1]
    const titleMatch = block.match(titleRegex)
    const linkMatch = block.match(linkRegex)
    if (titleMatch) {
      const title = titleMatch[1].trim()
      const link = linkMatch ? linkMatch[1] : ''
      const fullUrl = link && !link.startsWith('http') ? `${SOURCES[source]}${link}` : link
      articles.push({
        title,
        source_url: fullUrl,
        source: source,
        cefr_level: tagDifficulty(title),
        content_type: 'news_article',
      })
    }
  }
  return articles
}

Deno.serve(async (req) => {
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders })
  }

  try {
    const { source } = await req.json()
    const url = SOURCES[source]
    if (!url) {
      return new Response(
        JSON.stringify({ error: 'Unknown source' }),
        { status: 400, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      )
    }

    const resp = await fetch(url, {
      headers: { 'User-Agent': 'EnglishCoachPro/1.0' },
    })
    const html = await resp.text()
    const articles = extractArticles(html, source)

    return new Response(
      JSON.stringify({ articles }),
      { headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    )
  } catch (error) {
    return new Response(
      JSON.stringify({ error: error.message || 'Fetch failed' }),
      {
        status: 500,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
      }
    )
  }
})
