import { RequestHandler } from 'express';

// This middleware injects a helper in res.locals so templates can render scripts with data-cookie-category and they
// will not be immediately included unless consent cookie allows it. It doesn't mutate response body here, templates
// should use data-src instead of src to defer loading.
export const cookieConsentMiddleware: RequestHandler = (req:any, res, next) => {
  // helper to check consent from cookie
  res.locals.cookieConsent = function(){
    try{
      const c = (req.headers.cookie || '').split(';').map((s:string)=>s.trim()).find((s:any)=>s.startsWith('linkbay_cookie_consent='));
      if(!c) return { necessary: true, analytics: false, marketing: false };
      return JSON.parse(decodeURIComponent(c.split('=')[1]));
    }catch(e){ return { necessary: true, analytics: false, marketing: false }; }
  };
  next();
};

export default cookieConsentMiddleware;
