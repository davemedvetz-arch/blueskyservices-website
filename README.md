# Blue Sky Services — Website

Static website for Blue Sky Services, a family-run general contractor in Raleigh, NC (since 1996).

Live site: https://blueskyservices.pplx.app

## Structure

- `index.html` — Homepage
- `residential.html` — Home remodeling services
- `commercial.html` — Commercial construction services
- `about.html` — Company story
- `contact.html` — Contact page with estimate request form
- `review.html` — Unlisted review-request page (noindex)
- `style.css` / `base.css` — Styles (light/dark theme via `data-theme`)
- `app.js` — Interactivity: theme toggle (cookie-persisted), mobile menu, scroll reveal, FAQ accordion, contact form (opens pre-filled email)
- `assets/img/` — Logos and photography
- `build/` — Page templates and build script used during development

## Notes

- Pure static site — no backend or build step required to serve; host the root directory on any static host.
- The contact form opens the visitor's email client with a pre-filled message to info@blueskyservices.com.
- `sitemap.xml` and canonical URLs point to www.blueskyservices.com for production SEO.
