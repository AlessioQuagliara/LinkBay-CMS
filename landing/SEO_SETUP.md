# SEO Setup per LinkBay CMS Landing

## 📄 File implementati

### `/public/sitemap.xml`
Sitemap XML statica che include tutte le rotte principali del landing con:
- **Priority**: Homepage (1.0) → Features/Pricing (0.8) → About/Contact/Marketplace (0.6) → Blog/API-docs (0.5) → Work-with-us (0.4) → Auth pages (0.3) → Legal pages (0.2)
- **Change frequency**: Daily (blog) → Weekly (home, api-docs, marketplace) → Monthly (features, pricing, about, contact, work-with-us) → Yearly (auth, legal)
- **Last modified**: Data corrente (aggiornare manualmente)

### `/public/robots.txt`
File robots.txt configurato per:
- **Allow all** in produzione
- **Disallow percorsi sensibili**: `/api/*`, `/admin/*`, `/*.json`, `/login`, `/register`
- **Bot specifici**: Googlebot, Bingbot, Facebook, Twitter, LinkedIn
- **Sitemap reference**: Punta alla sitemap del dominio corrente

## 🚀 Test degli endpoint

### Verificare sitemap
```bash
curl -i http://localhost:3001/sitemap.xml
```
**Expected**: HTTP 200 + XML valido con Content-Type: text/xml

### Verificare robots
```bash
curl -i http://localhost:3001/robots.txt  
```
**Expected**: HTTP 200 + Plain text con Content-Type: text/plain

## ⚡ Come aggiornare la sitemap

### 1. Aggiungere nuove rotte statiche
Modificare `/public/sitemap.xml` aggiungendo:
```xml
<url>
  <loc>http://localhost:3001/nuova-pagina</loc>
  <lastmod>2025-09-24</lastmod>
  <changefreq>monthly</changefreq>
  <priority>0.6</priority>
</url>
```

### 2. Aggiornare URL per produzione
Sostituire `http://localhost:3001` con il dominio di produzione:
```xml
<loc>https://linkbay-cms.com/</loc>
```

### 3. Aggiornare date di modifica
Cambiare `<lastmod>2025-09-24</lastmod>` con la data corrente quando si modifica contenuto.

## 🔄 Rendere la sitemap dinamica (futuro)

### Opzione A: Build-time generation
1. Creare script Node.js che legge le rotte da `App.tsx`
2. Generare `sitemap.xml` durante `npm run build`
3. Includere nello script di CI/CD

### Opzione B: API backend integration
1. Endpoint backend `/api/sitemap-routes` che restituisce JSON delle rotte
2. Usare i hook React creati (`useSitemap.ts`) per fetch durante build
3. Script che genera file statico da API response

### Opzione C: Server-side generation
1. Spostare la logica nel backend Express
2. Servire `/sitemap.xml` dinamicamente dal backend
3. Includere contenuti dal database (articoli blog, landing pages custom)

## 📝 Utilizzo degli hook creati

Gli hook in `/src/hooks/useSitemap.ts` e `/src/utils/robots.ts` sono pronti per implementazione dinamica:

```typescript
// Esempio per generare sitemap dinamica
import { useSitemap } from '../hooks/useSitemap';

const { generateFullSitemap } = useSitemap();
const xml = await generateFullSitemap(); // Include fetch da API
```

## 🌍 Configurazione per ambienti

### Sviluppo
- URL base: `http://localhost:3001`
- Robots: Allow all (per testing)

### Staging  
- URL base: `https://staging.linkbay-cms.com`
- Robots: Disallow all (prevenire indicizzazione)

### Produzione
- URL base: `https://linkbay-cms.com`  
- Robots: Allow all + regole specifiche per bot

## 🔧 Comandi utili

### Validare sitemap XML
```bash
xmllint --noout /Users/alessio/LinkBay-CMS/landing/public/sitemap.xml
```

### Test Google Search Console
1. Caricare sitemap su Google Search Console
2. URL: `https://tuodominio.com/sitemap.xml`
3. Verificare che tutte le URL siano indicizzabili

### Analizzare robots.txt
```bash
# Test con user-agent specifico
curl -A "Googlebot" http://localhost:3001/robots.txt
```

## 📊 SEO Best Practices implementate

- ✅ **Sitemap XML valida** secondo standard sitemaps.org
- ✅ **Robots.txt compliant** con regole per bot principali
- ✅ **Content-Type headers** corretti (text/xml, text/plain)
- ✅ **Priority logic** basata su importanza business
- ✅ **Change frequency** realistica per ogni tipo di pagina
- ✅ **Bot-specific rules** per Googlebot, social media crawlers
- ✅ **Security** - percorsi sensibili bloccati