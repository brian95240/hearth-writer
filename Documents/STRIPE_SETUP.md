# Hearth Writer - Stripe Payment System Setup

> **Status:** ✅ LIVE - Fully configured and ready to accept payments  
> **Last Updated:** January 5, 2026  
> **Strategy:** Zero-code, fully automated payment processing using Stripe Payment Links with professional branding.

---

## Overview

The payment system allows Hearth Writer to sell licenses 24/7 without manual intervention:

1. **Customer** clicks payment link on landing page
2. **Stripe Payment Link** handles checkout (no code required)
3. **Stripe** processes payment, shows "HEARTH WRITER" on credit card statement
4. **Customer** receives confirmation and is redirected to welcome page
5. **Customer** uses installation wizard to activate Hearth Writer
6. **Customer** can manage subscription via Customer Portal

---

## Live Configuration

### Stripe Account Details

| Field | Value |
|-------|-------|
| **Account ID** | `acct_1RZUk82KS3i05iH4` |
| **Mode** | Live |
| **Statement Descriptor** | `HEARTH WRITER` |
| **Business Website** | https://brian95240.github.io/hearth-writer/ |

---

## Products & Pricing (Separate Products for Plan Switching)

> **Important:** Products are set up as separate items to enable plan switching in the Customer Portal.

### Hearth Writer - Architect ($19/month)

| Field | Value |
|-------|-------|
| **Product ID** | `prod_TjlOOiXNSPjC2f` |
| **Price ID** | `price_1SmHrr2KS3i05iH4ALz36ZZj` |
| **Payment Link** | https://buy.stripe.com/28E00cf5P3AB3uKggN0VO02 |
| **Features** | Multi-LORA mixing, Timeline injection, Advanced AI features |

### Hearth Writer - Showrunner ($49/month)

| Field | Value |
|-------|-------|
| **Product ID** | `prod_TjlOL5m0hKvzHb` |
| **Price ID** | `price_1SmHs32KS3i05iH4Yu7AXIX1` |
| **Payment Link** | https://buy.stripe.com/aFa7sE1eZ4EF4yOfcJ0VO03 |
| **Features** | Team dashboards, Legal indemnity, Custom grammars, Enterprise support |

---

## Customer Portal

| Field | Value |
|-------|-------|
| **Portal Link** | https://billing.stripe.com/p/login/14A6oAcXHfjje9o3u10VO00 |
| **Status** | ✅ Active |
| **Website Location** | Footer → "Manage Subscription" |

### Portal Features Enabled:

- ✅ Update payment methods (add/remove cards)
- ✅ View invoice history
- ✅ Update customer information (billing address)
- ✅ Cancel subscription (at end of billing period)
- ✅ Switch between Architect and Showrunner plans
- ✅ Prorate charges when switching plans
- ✅ Update immediately when switching to cheaper plan

---

## Payment Methods Enabled

**Profile Name:** Low Friction, Low Fees, on page engagement, no redirects

| Method | Status | Region |
|--------|--------|--------|
| Cards | ✅ Enabled | All regions |
| Cartes Bancaires | ✅ Enabled | France |
| Apple Pay | ✅ Enabled | All regions |
| Google Pay | ✅ Enabled | All regions |
| Link | ✅ Enabled | All regions |

---

## Branding Colors

| Color | Hex Code | Use |
|-------|----------|-----|
| **Primary (Warm Orange)** | `#D4692B` | Buttons, accents, highlights |
| **Secondary (Deep Brown)** | `#3D2314` | Text, headers, backgrounds |

**Logo:** Fireplace with pen icon (optimized to 227KB for Stripe upload)

---

## Integration with Website

### Payment Buttons (in `docs/index.html`)

```html
<!-- Architect Button -->
<a href="https://buy.stripe.com/28E00cf5P3AB3uKggN0VO02" class="cta-button">Subscribe - $19/mo</a>

<!-- Showrunner Button -->
<a href="https://buy.stripe.com/aFa7sE1eZ4EF4yOfcJ0VO03" class="cta-button">Subscribe - $49/mo</a>
```

### Footer Links

```html
<a href="https://billing.stripe.com/p/login/14A6oAcXHfjje9o3u10VO00" target="_blank">Manage Subscription</a>
```

---

## License Key System

### Key Format

```
HRTH_[TIER]_[RANDOM_ID]

Examples:
- HRTH_ARCHITECT_7x9K2mPq4R
- HRTH_SHOWRUNNER_Ent5Bz8Lw3
```

### Generating Keys

```bash
# Generate Architect key
echo "HRTH_ARCHITECT_$(openssl rand -base64 12 | tr -dc 'a-zA-Z0-9' | head -c 12)"

# Generate Showrunner key
echo "HRTH_SHOWRUNNER_$(openssl rand -base64 12 | tr -dc 'a-zA-Z0-9' | head -c 12)"
```

### Key Registry

See `Documents/LICENSE_KEYS.md` for issued keys.

---

## Customer Journey

1. **Discovery:** Customer visits https://brian95240.github.io/hearth-writer/
2. **Purchase:** Clicks "Subscribe" → Stripe Payment Link
3. **Checkout:** Enters payment info (Cards, Apple Pay, Google Pay, or Link)
4. **Confirmation:** Redirected to welcome page with license key
5. **Installation:** Uses wizard at `/install.html` for guided setup
6. **Activation:** Enters license key, creates desktop shortcut
7. **Management:** Uses Customer Portal to update payment, switch plans, or cancel

---

## Quick Links

| Resource | URL |
|----------|-----|
| Stripe Dashboard | https://dashboard.stripe.com |
| Products | https://dashboard.stripe.com/products |
| Customers | https://dashboard.stripe.com/customers |
| Subscriptions | https://dashboard.stripe.com/subscriptions |
| Payment Links | https://dashboard.stripe.com/payment-links |
| Customer Portal Settings | https://dashboard.stripe.com/settings/billing/portal |
| Branding Settings | https://dashboard.stripe.com/settings/branding |
| Payment Methods | https://dashboard.stripe.com/settings/payment_methods |

---

## Legacy Products (Should Be Archived)

These were created initially but replaced with separate products for plan switching:

| Product | Product ID | Price IDs | Status |
|---------|------------|-----------|--------|
| Hearth Writer (combined) | `prod_Tjb2XJH66ThMPT` | `price_1Sm7qc...`, `price_1Sm7qg...` | ⚠️ Archive |

To archive: Products → Find "Hearth Writer" → Archive

---

## Pricing Summary

| Tier | Price | Billing | Statement Descriptor | Status |
|------|-------|---------|---------------------|--------|
| Ronin | $0 | Free | N/A | ✅ Available |
| Architect | $19/mo | Monthly recurring | HEARTH WRITER | ✅ Live |
| Showrunner | $49/mo | Monthly recurring | HEARTH WRITER | ✅ Live |

---

## Troubleshooting

### Customer can't switch plans
- Verify both Architect and Showrunner products are added in Customer Portal settings
- Products must be separate (not two prices under one product)

### Statement descriptor issues
- Max 22 characters
- No special characters except `.` `-` `'`
- Must be recognizable to customer

### Customer doesn't see payment methods
- Verify payment methods are enabled in **Live mode** (not just Test mode)
- Check that the payment method configuration is set to "Active"

---

## Support

- **Stripe Documentation:** https://stripe.com/docs/payment-links
- **Hearth Writer Repository:** https://github.com/brian95240/hearth-writer
- **Business Website:** https://brian95240.github.io/hearth-writer/

---

*Unmanned. Automated. Professional.*
