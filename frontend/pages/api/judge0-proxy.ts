import type { NextApiRequest, NextApiResponse } from 'next';

// IMPORTANT: Store your RapidAPI key securely, e.g., in an environment variable
const RAPIDAPI_KEY = process.env.RAPIDAPI_KEY;
const RAPIDAPI_HOST = 'judge0-ce.p.rapidapi.com';

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  if (!RAPIDAPI_KEY) {
    return res.status(500).json({ error: 'RapidAPI key not configured on server' });
  }

  const { language_id, source_code, stdin } = req.body;

  if (!language_id || !source_code) {
    return res.status(400).json({ error: 'Missing language_id or source_code' });
  }

  try {
    const judge0Res = await fetch(`https://${RAPIDAPI_HOST}/submissions?base64_encoded=true&wait=true`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-RapidAPI-Key': RAPIDAPI_KEY,
        'X-RapidAPI-Host': RAPIDAPI_HOST,
      },
      body: JSON.stringify({
        language_id,
        source_code: Buffer.from(source_code).toString('base64'),
        stdin: stdin ? Buffer.from(stdin).toString('base64') : '',
      }),
    });

    const data = await judge0Res.json();
    if (!judge0Res.ok) {
      return res.status(judge0Res.status).json({ error: data.message || 'Judge0 API error', details: data });
    }
    res.status(200).json(data);
  } catch (err: unknown) {
    const message = err instanceof Error ? err.message : 'Unknown error';
    res.status(500).json({ error: 'Failed to connect to Judge0', details: message });
  }
}
