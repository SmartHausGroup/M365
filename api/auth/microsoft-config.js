// Microsoft 365 OAuth Configuration
export const MICROSOFT_CONFIG = {
  // OAuth endpoints
  authUrl: 'https://login.microsoftonline.com',
  tokenUrl: 'https://login.microsoftonline.com/common/oauth2/v2.0/token',

  // API endpoints
  graphUrl: 'https://graph.microsoft.com/v1.0',

  // Required scopes for M365 access
  scopes: [
    'User.Read',                    // Read user profile
    'Sites.Read.All',              // Read SharePoint sites
    'Group.Read.All',              // Read Teams/Office 365 groups
    'Directory.Read.All',          // Read directory data
    'Calendars.Read',              // Read calendars
    'Mail.Read',                   // Read email
    'Mail.Send',                   // Send email
    'Files.Read.All'               // Read OneDrive files
  ],

  // Response types
  responseType: 'code',
  responseMode: 'query',

  // PKCE for security
  codeChallengeMethod: 'S256',

  // State parameter for security
  stateLength: 32,

  // Token expiration
  tokenExpiryBuffer: 300, // 5 minutes

  // Error handling
  errorRedirect: '/auth-error',

  // Success redirect
  successRedirect: '/dashboard'
};

// Helper function to generate PKCE challenge
export function generatePKCE() {
  const codeVerifier = generateRandomString(128);
  const codeChallenge = base64URLEncode(sha256(codeVerifier));
  return { codeVerifier, codeChallenge };
}

// Helper function to generate random string
function generateRandomString(length) {
  const possible = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-._~';
  let text = '';
  for (let i = 0; i < length; i++) {
    text += possible.charAt(Math.floor(Math.random() * possible.length));
  }
  return text;
}

// Helper function to base64 URL encode
function base64URLEncode(buffer) {
  return buffer.toString('base64')
    .replace(/\+/g, '-')
    .replace(/\//g, '_')
    .replace(/=/g, '');
}

// Helper function to SHA256 hash
async function sha256(message) {
  const msgBuffer = new TextEncoder().encode(message);
  const hashBuffer = await crypto.subtle.digest('SHA-256', msgBuffer);
  return new Uint8Array(hashBuffer);
}
