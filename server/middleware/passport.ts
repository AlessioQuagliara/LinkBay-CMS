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
    // ensure callback path is present; prefer an allowed uri that matches APP_URL, but append
    // the callback path if the allowed value is origin-only
    const callbackPath = '/auth/google/callback';
    let googleCallback = `${appUrl}${callbackPath}`;
    if (allowed.length) {
      // find allowed entry that refers to the same origin as APP_URL
      const match = allowed.find(u => u.startsWith(appUrl));
      const pick = match || allowed[0];
      // if pick already contains the callback path, use as-is, otherwise append
      if (pick.endsWith(callbackPath)) googleCallback = pick;
      else googleCallback = `${pick.replace(/\/$/, '')}${callbackPath}`;
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

  // Microsoft/Azure login removed per request

  passport.serializeUser((user: any, done) => done(null, user));
  passport.deserializeUser((obj: any, done) => done(null, obj));
}
