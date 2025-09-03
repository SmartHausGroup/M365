// Vercel serverless function for Microsoft OAuth callback
export default async function handler(req, res) {
  if (req.method !== 'GET') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    const { code, state, error } = req.query;
    
    if (error) {
      console.error('OAuth error:', error);
      return res.status(400).json({ 
        error: 'OAuth error',
        message: error
      });
    }

    if (!code) {
      console.error('Authorization code missing');
      return res.status(400).json({ 
        error: 'Authorization code missing',
        message: 'OAuth flow incomplete'
      });
    }

    // Decode state to get return URL and code verifier
    let returnUrl = '/';
    let codeVerifier = null;
    try {
      if (state) {
        const decodedState = JSON.parse(Buffer.from(state, 'base64').toString());
        returnUrl = decodedState.returnUrl || '/';
        codeVerifier = decodedState.codeVerifier;
        console.log('Decoded state:', { returnUrl, hasCodeVerifier: !!codeVerifier });
      }
    } catch (e) {
      console.warn('Failed to decode state:', e);
    }

    // If we have a real authorization code, exchange it for tokens
    if (code && codeVerifier) {
      try {
        console.log('Exchanging authorization code for tokens...');
        
        const clientId = process.env.MICROSOFT_CLIENT_ID;
        const clientSecret = process.env.MICROSOFT_CLIENT_SECRET;
        const redirectUri = process.env.MICROSOFT_REDIRECT_URI || 'https://m365.smarthaus.ai/api/auth/callback';
        
        if (!clientId || !clientSecret) {
          throw new Error('Microsoft OAuth credentials not configured');
        }

        // Exchange authorization code for access token
        const tokenResponse = await fetch('https://login.microsoftonline.com/common/oauth2/v2.0/token', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
          },
          body: new URLSearchParams({
            client_id: clientId,
            client_secret: clientSecret,
            code: code,
            code_verifier: codeVerifier,
            redirect_uri: redirectUri,
            grant_type: 'authorization_code',
          }),
        });

        if (!tokenResponse.ok) {
          const errorText = await tokenResponse.text();
          console.error('Token exchange failed:', errorText);
          throw new Error(`Token exchange failed: ${tokenResponse.status}`);
        }

        const tokenData = await tokenResponse.json();
        console.log('Token exchange successful, got access token');
        
        // Store tokens securely (in production, use secure storage)
        // For now, we'll redirect with the access token
        const accessToken = tokenData.access_token;
        const redirectUrl = `${returnUrl}#token=${encodeURIComponent(accessToken)}&type=real`;
        
        return res.redirect(redirectUrl);
        
      } catch (tokenError) {
        console.error('Token exchange error:', tokenError);
        // Fall back to demo mode
        console.log('Falling back to demo mode due to token exchange error');
      }
    }

    // Fallback to demo mode
    console.log('Using demo mode - generating demo token');
    const demoToken = Buffer.from(`demo_${Date.now()}`).toString('base64');
    const redirectUrl = `${returnUrl}#token=${encodeURIComponent(demoToken)}&type=demo`;
    
    // Redirect back to dashboard with token
    res.redirect(redirectUrl);
    
  } catch (error) {
    console.error('Callback endpoint error:', error);
    res.status(500).json({ 
      error: 'Authentication callback failed',
      message: 'Please try again'
    });
  }
}
