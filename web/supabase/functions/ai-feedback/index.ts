// Supabase Edge Function: AI Writing Feedback (Claude API proxy)
// Deploy: supabase functions deploy ai-feedback

import Anthropic from 'npm:@anthropic-ai/sdk@0.30.1'

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
}

Deno.serve(async (req) => {
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders })
  }

  try {
    const { exam_type, task_prompt, essay } = await req.json()

    const client = new Anthropic({
      apiKey: Deno.env.get('ANTHROPIC_API_KEY')!,
    })

    const message = await client.messages.create({
      model: 'claude-sonnet-4-6',
      max_tokens: 1500,
      messages: [
        {
          role: 'user',
          content: `You are an expert ${exam_type} examiner. Evaluate this writing response.
Task: ${task_prompt}
Essay: ${essay}

Respond ONLY with a JSON object (no markdown, no preamble):
{
  "band_estimate": number,
  "task_achievement": { "score": number, "feedback": string },
  "coherence": { "score": number, "feedback": string },
  "lexical_resource": { "score": number, "feedback": string, "suggestions": string[] },
  "grammar_range": {
    "score": number,
    "corrections": [{ "original": string, "corrected": string, "explanation": string }]
  },
  "rewritten_paragraph": string,
  "overall_tip": string
}`,
        },
      ],
    })

    // Extract text from response
    const textBlock = message.content.find((b: any) => b.type === 'text')
    const responseText = textBlock?.text || '{}'

    let parsed: any
    try {
      parsed = JSON.parse(responseText)
    } catch {
      parsed = { raw_feedback: responseText }
    }

    return new Response(JSON.stringify(parsed), {
      headers: { ...corsHeaders, 'Content-Type': 'application/json' },
    })
  } catch (error) {
    return new Response(
      JSON.stringify({ error: error.message || 'AI feedback failed' }),
      {
        status: 500,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
      }
    )
  }
})
