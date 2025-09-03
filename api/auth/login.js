// Vercel serverless function for Microsoft 365 OAuth login
export default async function handler(req, res) {
  if (req.method !== 'GET') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    const { r: returnUrl = '/' } = req.query;
    
    // Microsoft 365 OAuth configuration
    const clientId = process.env.MICROSOFT_CLIENT_ID;
    const redirectUri = process.env.MICROSOFT_REDIRECT_URI || 'https://m365.smarthaus.ai/api/auth/callback';
    
    // Required scopes for M365 access
    const scopes = [
      'User.Read',                    // Read user profile
      'Sites.Read.All',              // Read SharePoint sites
      'Group.Read.All',              // Read Teams/Office 365 groups
      'Directory.Read.All',          // Read directory data
      'Calendars.Read',              // Read calendars
      'Mail.Read',                   // Read email
      'Files.Read.All'               // Read OneDrive files
    ];
    
    if (!clientId) {
      // Demo mode - redirect to callback with demo token
      console.log('Microsoft OAuth not configured, using demo mode');
      const demoToken = Buffer.from(`demo_${Date.now()}`).toString('base64');
      const redirectUrl = `${returnUrl}#token=${encodeURIComponent(demoToken)}`;
      return res.redirect(redirectUrl);
    }

    // Real Microsoft OAuth flow
    console.log('Initiating Microsoft OAuth flow...');
    
    // Generate PKCE challenge for security
    const codeVerifier = generateRandomString(128);
    const codeChallenge = await generateCodeChallenge(codeVerifier);
    
    // Store code verifier in state parameter (in production, use Redis/database)
    const stateData = {
      returnUrl,
      codeVerifier,
      timestamp: Date.now()
    };
    const state = Buffer.from(JSON.stringify(stateData)).toString('base64');
    
    // Build Microsoft OAuth URL with proper parameters
    const authUrl = new URL('https://login.microsoftonline.com/common/oauth2/v2.0/authorize');
    authUrl.searchParams.set('client_id', clientId);
    authUrl.searchParams.set('response_type', 'code');
    authUrl.searchParams.set('redirect_uri', redirectUri);
    authUrl.searchParams.set('scope', scopes.join(' '));
    authUrl.searchParams.set('response_mode', 'query');
    authUrl.searchParams.set('state', state);
    authUrl.searchParams.set('code_challenge', codeChallenge);
    authUrl.searchParams.set('code_challenge_method', 'S256');
    
    console.log('Redirecting to Microsoft OAuth:', authUrl.toString());
    
    // Redirect to Microsoft OAuth - this will show the Microsoft login popup
    res.redirect(authUrl.toString());
    
  } catch (error) {
    console.error('Login endpoint error:', error);
    res.status(500).json({ 
      error: 'Authentication service unavailable',
      message: 'Please try again later'
    });
  }
}

// Helper function to generate random string for PKCE
function generateRandomString(length) {
  const possible = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-._~';
  let text = '';
  for (let i = 0; i < length; i++) {
    text += possible.charAt(Math.floor(Math.random() * possible.length));
  }
  return text;
}

// Helper function to generate PKCE code challenge
async function generateCodeChallenge(codeVerifier) {
  const encoder = new TextEncoder();
  const data = encoder.encode(codeVerifier);
  const digest = await crypto.subtle.digest('SHA-256', data);
  return base64URLEncode(digest);
}

// Helper function to base64 URL encode
function base64URLEncode(buffer) {
  return Buffer.from(buffer)
    .toString('base64')
    .replace(/\+/g, '-')
    .replace(/\//g, '_')
    .replace(/=/g, '');
}
