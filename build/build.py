#!/usr/bin/env python3
"""Static site builder for Blue Sky Services.

Assembles pages from build/template.html + build/pages/*.html fragments,
injecting per-page SEO metadata, JSON-LD schema, navigation and breadcrumbs.
Also emits sitemap.xml and robots.txt.
"""
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUILD = os.path.join(ROOT, "build")

with open(os.path.join(BUILD, "meta.json")) as f:
    META = json.load(f)

SITE = META["site"]
BASE = SITE["base_url"]
OG_IMAGE = BASE + "/assets/img/hero-jobsite.jpg"

with open(os.path.join(BUILD, "template.html")) as f:
    TEMPLATE = f.read()


# ---------------------------------------------------------------- schema
def local_business_schema():
    return {
        "@type": ["GeneralContractor", "LocalBusiness"],
        "@id": BASE + "/#organization",
        "name": SITE["name"],
        "alternateName": "Blue Sky Services Construction",
        "url": BASE + "/",
        "logo": BASE + "/assets/img/logo-original.png",
        "image": OG_IMAGE,
        "telephone": SITE["phone"],
        "faxNumber": SITE["fax"],
        "email": SITE["email"],
        "foundingDate": SITE["founded"],
        "founder": {"@type": "Person", "name": "David Medvetz"},
        "priceRange": "$$",
        "description": (
            "Blue Sky Services is a family-run Raleigh, NC general contractor founded in 1996, "
            "providing residential home remodeling, commercial construction and tenant upfits, "
            "land development, and real estate investment opportunities across the Triangle."
        ),
        "address": {
            "@type": "PostalAddress",
            "streetAddress": SITE["street"],
            "addressLocality": SITE["city"],
            "addressRegion": SITE["state"],
            "postalCode": SITE["zip"],
            "addressCountry": "US",
        },
        "geo": {"@type": "GeoCoordinates", "latitude": 35.8073, "longitude": -78.5795},
        "openingHoursSpecification": [
            {
                "@type": "OpeningHoursSpecification",
                "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
                "opens": "08:00",
                "closes": "17:00",
            }
        ],
        "areaServed": [
            {"@type": "City", "name": n}
            for n in [
                "Raleigh", "Cary", "Apex", "Wake Forest", "Garner", "Knightdale",
                "Holly Springs", "Fuquay-Varina", "Morrisville", "Clayton",
                "Durham", "Chapel Hill", "Wendell", "Zebulon",
            ]
        ],
        "sameAs": [
            "https://www.facebook.com/BlueSkyEricBursky/",
            "https://www.instagram.com/blueskyconstruction/",
            "https://www.linkedin.com/company/blue-sky-services-commercial-construction",
        ],
        "hasOfferCatalog": {
            "@type": "OfferCatalog",
            "name": "Construction & Development Services",
            "itemListElement": [
                {"@type": "Offer", "itemOffered": {"@type": "Service", "name": n}}
                for n in [
                    "Kitchen Remodeling", "Bathroom Remodeling", "Home Additions",
                    "Sunroom Construction", "Deck and Porch Building",
                    "Basement and Attic Finishing", "Commercial Tenant Upfits",
                    "Office Build-Outs", "Retail and Restaurant Construction",
                    "Land Development", "Multi-Family Development",
                ]
            ],
        },
    }


def website_schema():
    return {
        "@type": "WebSite",
        "@id": BASE + "/#website",
        "url": BASE + "/",
        "name": SITE["name"],
        "publisher": {"@id": BASE + "/#organization"},
        "inLanguage": "en-US",
    }


def breadcrumb_schema(crumbs):
    items = [{
        "@type": "ListItem", "position": 1, "name": "Home", "item": BASE + "/",
    }]
    for i, (label, href) in enumerate(crumbs, start=2):
        items.append({
            "@type": "ListItem", "position": i, "name": label,
            "item": "%s/%s" % (BASE, href),
        })
    return {"@type": "BreadcrumbList", "itemListElement": items}


def service_schema(name, description, service_type, page):
    return {
        "@type": "Service",
        "name": name,
        "serviceType": service_type,
        "description": description,
        "provider": {"@id": BASE + "/#organization"},
        "url": "%s/%s" % (BASE, page),
        "areaServed": {
            "@type": "AdministrativeArea",
            "name": "The Triangle, North Carolina",
        },
    }


def faq_schema(pairs):
    return {
        "@type": "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name": q,
                "acceptedAnswer": {"@type": "Answer", "text": a},
            }
            for q, a in pairs
        ],
    }


RESIDENTIAL_FAQ = [
    ("How much does a kitchen remodel cost in Raleigh, NC?",
     "Most full kitchen remodels in the Raleigh area land somewhere between a modest refresh and a full "
     "gut-and-rebuild, and the range is wide because cabinets, countertops and layout changes drive the "
     "number. We walk your kitchen, talk through what you actually want, and hand you a written line-item "
     "estimate for free so you are working from real numbers instead of a guess."),
    ("How long does a bathroom remodel take?",
     "A straightforward bathroom remodel typically runs a few weeks from demo to final walkthrough. "
     "Bigger jobs that move plumbing, change the footprint, or involve custom tile take longer. We give "
     "you a written schedule before we start and tell you right away if anything shifts."),
    ("Are you licensed and insured?",
     "Yes. Blue Sky Services is a North Carolina licensed general contractor and carries $2 million in "
     "liability insurance. We are also a Certified Green Remodeler. We are happy to send documentation "
     "before you sign anything."),
    ("Do you offer financing for home remodeling?",
     "We do help homeowners arrange financing for remodeling projects. Tell us your budget target during "
     "the estimate and we will walk you through the options available."),
    ("What areas around Raleigh do you serve?",
     "We work throughout the Triangle, including Raleigh, Cary, Apex, Wake Forest, Garner, Knightdale, "
     "Holly Springs, Fuquay-Varina, Morrisville, Clayton, Wendell, Zebulon, Durham and Chapel Hill."),
    ("Will I have one person to talk to during my project?",
     "Yes. You get a single point of contact from the first estimate through the final walkthrough. You "
     "will never be handed off to a call center or left wondering who is showing up tomorrow."),
]

COMMERCIAL_FAQ = [
    ("Can you keep my business open during construction?",
     "In most cases, yes. We regularly phase tenant upfits and remodels so occupied retail, office and "
     "medical spaces keep operating. We schedule loud or disruptive work around your hours and coordinate "
     "with building management on access, deliveries and shared spaces."),
    ("How fast can you deliver a tenant upfit?",
     "Speed is one of the reasons national brands keep hiring us. Once permits are in hand, our fast-track "
     "delivery approach compresses the schedule by overlapping trades and pre-ordering long-lead items. "
     "We recently completed a 20,000+ square foot restoration in two weeks."),
    ("Do you handle permitting and inspections?",
     "Yes. We manage permits, inspections and code compliance as part of the contract, and we are your "
     "single point of responsibility from drawings through final sign-off."),
    ("What types of commercial projects do you take on?",
     "Office build-outs and upfits, retail stores, restaurants, medical and dental suites, schools, "
     "multi-family interiors and common areas, and full commercial restorations after storm or fire damage."),
    ("Do you work with national or multi-site brands?",
     "We do. Blue Sky has completed work for more than 50 national commercial clients including Chipotle, "
     "GAP, FedEx and Old Navy, and we understand brand standards, rollout schedules and corporate reporting."),
]

INVESTOR_FAQ = [
    ("How do I invest?",
     "Start by requesting more information through our contact form. After reviewing offering documents and "
     "completing a subscription, your investment is reviewed by an SEC-regulated fund administrator. Funds "
     "are held in escrow until the offering is fully funded, then released to the project."),
    ("Is there a minimum investment?",
     "Yes. Each individual offering states its own minimum investment requirement in its offering documents."),
    ("Can I invest through an LLC or trust?",
     "Yes. Investing through an LLC, trust or other business entity is allowed, though additional "
     "documentation is required during onboarding."),
    ("How is my financial information protected?",
     "All communication is encrypted via HTTPS/SSL/TLS. Escrow, background checks and document signing are "
     "handled by outsourced, SEC-compliant partners disclosed in each offering's documents."),
]

PAGE_SCHEMA = {
    "residential.html": [
        service_schema(
            "Home Remodeling in Raleigh, NC",
            "Kitchen remodeling, bathroom renovation, home additions, sunrooms, basements, decks and "
            "porches for homeowners throughout Raleigh and the Triangle.",
            "Residential Remodeling", "residential.html"),
        faq_schema(RESIDENTIAL_FAQ),
    ],
    "commercial.html": [
        service_schema(
            "Commercial Construction and Tenant Upfits in Raleigh, NC",
            "Commercial general contracting, tenant upfits, office build-outs, retail, restaurant and "
            "medical construction throughout the Triangle region of North Carolina.",
            "Commercial General Contracting", "commercial.html"),
        faq_schema(COMMERCIAL_FAQ),
    ],
    "development.html": [
        service_schema(
            "Land Development and Ground-Up Construction",
            "Land acquisition, entitlement, principal and fee development for multi-family, mixed-use, "
            "retail and build-to-suit projects across North Carolina.",
            "Real Estate Development", "development.html"),
    ],
    "investors.html": [faq_schema(INVESTOR_FAQ)],
    "contact.html": [{
        "@type": "ContactPage",
        "url": BASE + "/contact.html",
        "name": "Contact Blue Sky Services",
        "about": {"@id": BASE + "/#organization"},
    }],
}


# ---------------------------------------------------------------- nav
def build_nav(current):
    desktop, mobile = [], []
    for item in META["nav"]:
        active = ' class="is-active" aria-current="page"' if item["file"] == current else ""
        desktop.append('      <a href="./%s"%s>%s</a>' % (item["file"], active, item["label"]))
        mobile.append('    <a href="./%s"%s>%s</a>' % (item["file"], active, item["label"]))
    return "\n".join(desktop), "\n".join(mobile)


def build_breadcrumb(crumbs):
    if not crumbs:
        return ""
    links = ['<a href="./index.html">Home</a>']
    for label, href in crumbs[:-1]:
        links.append('<a href="./%s">%s</a>' % (href, label))
    links.append('<span aria-current="page">%s</span>' % crumbs[-1][0])
    sep = '<span class="crumb-sep" aria-hidden="true">/</span>'
    return (
        '<nav class="breadcrumb" aria-label="Breadcrumb"><div class="container">'
        + sep.join(links) + "</div></nav>"
    )


# ---------------------------------------------------------------- build
def build():
    out_files = []
    for page, cfg in META["pages"].items():
        frag_path = os.path.join(BUILD, "pages", page)
        with open(frag_path) as f:
            content = f.read()

        graph = [local_business_schema(), website_schema()]
        if cfg["breadcrumb"]:
            graph.append(breadcrumb_schema(cfg["breadcrumb"]))
        graph.extend(PAGE_SCHEMA.get(page, []))

        schema_json = json.dumps(
            {"@context": "https://schema.org", "@graph": graph},
            indent=2, ensure_ascii=False,
        )
        schema_block = '<script type="application/ld+json">\n%s\n</script>' % schema_json

        canonical = BASE + "/" + ("" if page == "index.html" else page)
        desktop_nav, mobile_nav = build_nav(page)

        html = TEMPLATE
        for key, val in [
            ("{{TITLE}}", cfg["title"]),
            ("{{DESCRIPTION}}", cfg["description"]),
            ("{{KEYWORDS}}", cfg["keywords"]),
            ("{{CANONICAL}}", canonical),
            ("{{OG_IMAGE}}", OG_IMAGE),
            ("{{SCHEMA}}", schema_block),
            ("{{ROBOTS}}", "noindex, nofollow" if cfg.get("noindex")
             else "index, follow, max-image-preview:large"),
            ("{{NAV_LINKS}}", desktop_nav),
            ("{{MOBILE_NAV_LINKS}}", mobile_nav),
            ("{{HEADER_SOLID}}", " header-solid" if page == "contact.html" else ""),
            ("{{CONTENT}}", content.replace("<!--BREADCRUMB-->", build_breadcrumb(cfg["breadcrumb"]))),
        ]:
            html = html.replace(key, val)

        with open(os.path.join(ROOT, page), "w") as f:
            f.write(html)
        out_files.append(page)

    # sitemap
    urls = []
    for page, cfg in META["pages"].items():
        if cfg.get("noindex"):
            continue
        loc = BASE + "/" + ("" if page == "index.html" else page)
        urls.append(
            "  <url>\n    <loc>%s</loc>\n    <changefreq>monthly</changefreq>\n"
            "    <priority>%s</priority>\n  </url>" % (loc, cfg["priority"])
        )
    sitemap = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "\n".join(urls) + "\n</urlset>\n"
    )
    with open(os.path.join(ROOT, "sitemap.xml"), "w") as f:
        f.write(sitemap)

    robots = (
        "User-agent: *\n"
        "Allow: /\n\n"
        "Sitemap: %s/sitemap.xml\n" % BASE
    )
    with open(os.path.join(ROOT, "robots.txt"), "w") as f:
        f.write(robots)

    print("Built %d pages: %s" % (len(out_files), ", ".join(sorted(out_files))))
    print("Wrote sitemap.xml and robots.txt")


if __name__ == "__main__":
    build()
