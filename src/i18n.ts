import i18next from 'i18next';
import Backend from 'i18next-fs-backend';
import middleware from 'i18next-http-middleware';
import path from 'path';

const localesPath = path.join(__dirname, '..', 'locales');

i18next
  .use(Backend)
  .use(middleware.LanguageDetector)
  .init({
    fallbackLng: 'en',
    preload: ['en','it','es'],
    ns: ['common'],
    defaultNS: 'common',
    backend: {
      loadPath: path.join(localesPath, '{{lng}}/{{ns}}.json')
    },
    detection: {
      order: ['querystring','header'],
      lookupQuerystring: 'lang',
      caches: []
    },
    interpolation: { escapeValue: false }
  });

export { i18next as i18n, middleware };
