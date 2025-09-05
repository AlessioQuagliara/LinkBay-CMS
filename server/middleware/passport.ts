import passport from 'passport';
import { Strategy as GoogleStrategy } from 'passport-google-oauth20';
import { Strategy as GitHubStrategy } from 'passport-github2';
// passport-azure-ad doesn't provide clean TS types here; require at runtime
const AzureAdModule: any = require('passport-azure-ad');
const AzureAdStrategy = AzureAdModule.OIDCStrategy;

export default function setupPassport() {
  // Google
  if (process.env.GOOGLE_CLIENT_ID && process.env.GOOGLE_CLIENT_SECRET) {
    // parse allowed redirect URIs from env (comma separated)
    const appUrl = process.env.APP_URL || 'http://localhost:3001';
    const allowed = (process.env.GOOGLE_ALLOWED_REDIRECT_URIS || '').split(',').map(s => s.trim()).filter(Boolean);
    // choose a callback that matches APP_URL if present, otherwise first allowed, otherwise default to APP_URL
    let googleCallback = `${appUrl}/auth/google/callback`;
    if (allowed.length) {
      const match = allowed.find(u => u.startsWith(appUrl));
      googleCallback = match || allowed[0] + '/auth/google/callback';
    }

    passport.use(
      new GoogleStrategy(
        {
          clientID: process.env.GOOGLE_CLIENT_ID!,
          clientSecret: process.env.GOOGLE_CLIENT_SECRET!,
          callbackURL: googleCallback,
        },
  (accessToken: any, refreshToken: any, profile: any, done: any) => done(null, { profile, accessToken })
      )
    );
  }

  // GitHub
  if (process.env.GITHUB_CLIENT_ID && process.env.GITHUB_CLIENT_SECRET) {
    const githubCallback = process.env.GITHUB_CALLBACK_URL || `${process.env.APP_URL || 'http://localhost:3001'}/auth/github/callback`;
    passport.use(
      new GitHubStrategy(
        {
          clientID: process.env.GITHUB_CLIENT_ID!,
          clientSecret: process.env.GITHUB_CLIENT_SECRET!,
          callbackURL: githubCallback,
        },
  (accessToken: any, refreshToken: any, profile: any, done: any) => done(null, { profile, accessToken })
      )
    );
  }

  // Azure AD (Microsoft) - OIDC
  if (process.env.AZURE_CLIENT_ID && process.env.AZURE_CLIENT_SECRET && process.env.AZURE_TENANT_ID) {
    passport.use(
      new AzureAdStrategy(
        {
          identityMetadata: `https://login.microsoftonline.com/${process.env.AZURE_TENANT_ID}/v2.0/.well-known/openid-configuration`,
          clientID: process.env.AZURE_CLIENT_ID!,
          clientSecret: process.env.AZURE_CLIENT_SECRET!,
          responseType: 'code',
          responseMode: 'form_post',
          redirectUrl: process.env.AZURE_CALLBACK_URL || `${process.env.APP_URL || 'http://localhost:3001'}/auth/microsoft/callback`,
          allowHttpForRedirectUrl: true,
          scope: ['profile', 'email', 'openid'],
        },
  (iss: any, sub: any, profile: any, accessToken: any, refreshToken: any, done: any) => done(null, { profile, accessToken })
      )
    );
  }

  passport.serializeUser((user: any, done) => done(null, user));
  passport.deserializeUser((obj: any, done) => done(null, obj));
}
