const url = require('url');

const providers = {
  google: {
    name: 'google',
    authUrl: 'https://accounts.google.com/o/oauth2/v2/auth',
    scope: ['openid', 'profile', 'email'],
    clientIdEnv: 'GOOGLE_CLIENT_ID',
    clientSecretEnv: 'GOOGLE_CLIENT_SECRET',
    callbackPath: '/auth/google/callback',
  },
  github: {
    name: 'github',
    authUrl: 'https://github.com/login/oauth/authorize',
    scope: ['user:email'],
    clientIdEnv: 'GITHUB_CLIENT_ID',
    clientSecretEnv: 'GITHUB_CLIENT_SECRET',
    callbackPath: '/auth/github/callback',
  },
  microsoft: {
    name: 'microsoft',
    authUrl: 'https://login.microsoftonline.com/common/oauth2/v2.0/authorize',
    scope: ['openid', 'profile', 'email'],
    clientIdEnv: 'AZURE_CLIENT_ID',
    clientSecretEnv: 'AZURE_CLIENT_SECRET',
    callbackPath: '/auth/microsoft/callback',
  },
};

function getProvider(name) {
  return providers[name];
}

function generateAuthUrl(providerName, state = '') {
  const provider = getProvider(providerName);
  if (!provider) throw new Error('Unknown provider');

  const clientId = process.env[provider.clientIdEnv];
  const redirectUri = `${process.env.APP_URL || 'http://localhost:3001'}${provider.callbackPath}`;

  const params = {
    client_id: clientId,
    redirect_uri: redirectUri,
    response_type: 'code',
    scope: provider.scope.join(' '),
    state,
  };

  const authUrl = url.format({ pathname: provider.authUrl, query: params });
  return authUrl;
}

// handleCallback: normalize a passport/profile object to a unified user shape
function handleCallback(providerName, profile, accessToken) {
  if (!profile) return null;

  // Mapping common fields
  const mapped = {
    provider: providerName,
    providerId: profile.id || profile.sub || (profile.provider && profile.provider.id),
    displayName: profile.displayName || (profile.name && `${profile.name.givenName || ''} ${profile.name.familyName || ''}`.trim()),
    emails: (profile.emails && profile.emails.map((e) => e.value)) || (profile._json && profile._json.email ? [profile._json.email] : []),
    raw: profile,
    accessToken,
  };

  // Choose primary email if present
  mapped.email = mapped.emails && mapped.emails.length ? mapped.emails[0] : undefined;

  return mapped;
}

module.exports = { providers, getProvider, generateAuthUrl, handleCallback };
