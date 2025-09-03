// Vercel serverless function for getting authenticated user profile
export default async function handler(req, res) {
  if (req.method !== 'GET') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    // Get authorization header
    const authHeader = req.headers.authorization;
    
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      return res.status(401).json({ 
        error: 'Unauthorized',
        message: 'Valid access token required'
      });
    }

    const token = authHeader.substring(7);
    
    // Check if this is a demo token or real token
    if (token.startsWith('demo_')) {
      console.log('Using demo user profile');
      return res.status(200).json(getDemoUserProfile());
    }
    
    // Real Microsoft Graph API call
    try {
      console.log('Making Microsoft Graph API call for user profile...');
      
      const graphResponse = await fetch('https://graph.microsoft.com/v1.0/me', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (!graphResponse.ok) {
        console.error('Graph API call failed:', graphResponse.status, graphResponse.statusText);
        throw new Error(`Graph API failed: ${graphResponse.status}`);
      }

      const userData = await graphResponse.json();
      console.log('Successfully retrieved user profile from Microsoft Graph');
      
      // Transform Microsoft Graph data to our format
      const userProfile = {
        user: {
          displayName: userData.displayName || 'Unknown User',
          userPrincipalName: userData.userPrincipalName || 'unknown@domain.com',
          mail: userData.mail || userData.userPrincipalName || 'unknown@domain.com',
          jobTitle: userData.jobTitle || 'Unknown',
          companyName: userData.companyName || 'Unknown Company',
          department: userData.department || 'Unknown Department',
          officeLocation: userData.officeLocation || 'Unknown Location',
          businessPhones: userData.businessPhones || [],
          mobilePhone: userData.mobilePhone || 'Unknown',
          preferredLanguage: userData.preferredLanguage || 'en-US',
          id: userData.id || 'unknown-id'
        },
        permissions: [
          'm365.user',
          'graph.access',
          'profile.read'
        ],
        roles: ['Authenticated User'],
        lastSignIn: new Date().toISOString(),
        environment: 'production',
        source: 'microsoft_graph'
      };

      res.status(200).json(userProfile);
      
    } catch (graphError) {
      console.error('Microsoft Graph API error:', graphError);
      console.log('Falling back to demo profile due to Graph API error');
      
      // Fall back to demo profile
      res.status(200).json(getDemoUserProfile());
    }
    
  } catch (error) {
    console.error('User profile endpoint error:', error);
    res.status(500).json({ 
      error: 'Failed to retrieve user profile',
      message: 'Please try again'
    });
  }
}

// Demo user profile for fallback
function getDemoUserProfile() {
  return {
    user: {
      displayName: 'Philip Siniscalchi',
      userPrincipalName: 'philip@smarthaus.ai',
      mail: 'philip@smarthaus.ai',
      jobTitle: 'Founder & CEO',
      companyName: 'SmartHaus Group',
      department: 'Executive',
      officeLocation: 'Manalapan, NJ',
      businessPhones: ['+1-555-0123'],
      mobilePhone: '+1-555-0124',
      preferredLanguage: 'en-US',
      id: 'demo-user-12345'
    },
    permissions: [
      'm365.admin',
      'sharepoint.admin',
      'teams.admin',
      'research.access',
      'business.access'
    ],
    roles: ['Global Administrator', 'Research Lead', 'Business Owner'],
    lastSignIn: new Date().toISOString(),
    environment: 'demo',
    source: 'demo_fallback'
  };
}
