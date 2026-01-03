# Hearth Writer - Unmanned Payment System Setup

> **Strategy:** Zero-code, fully automated license key delivery using Stripe Payment Links with a dedicated sub-account for professional branding.

---

## Overview

The "Unmanned" system allows Hearth Writer to sell licenses 24/7 without manual intervention:

1. **Customer** clicks "Purchase Key" on landing page
2. **Stripe Payment Link** handles checkout (no code required)
3. **Stripe** processes payment, shows "HEARTH WRITER" on credit card statement
4. **Webhook** triggers license key delivery (or manual email for v1.0)
5. **Customer** receives key and activates Hearth Writer

---

## Step 1: Create Stripe Sub-Account (Connected Account)

Creating a dedicated sub-account ensures the customer's credit card statement shows **"HEARTH WRITER"** instead of your personal name. This:
- Reduces chargebacks (customers recognize the charge)
- Looks professional
- Separates business finances

### Option A: Stripe Express Account (Recommended)

1. Go to [Stripe Dashboard](https://dashboard.stripe.com)
2. Navigate to **Connect** → **Accounts**
3. Click **+ Create** → **Express account**
4. Fill in business details:
   - **Business name:** Hearth Writer
   - **Statement descriptor:** HEARTH WRITER
   - **Support email:** support@hearthwriter.dev
5. Complete identity verification
6. Note the **Account ID** (starts with `acct_`)

### Option B: Single Account with Custom Descriptor

If you prefer a single account:

1. Go to **Settings** → **Public details**
2. Set **Statement descriptor:** HEARTHWRITER (max 22 chars, no spaces)
3. Set **Shortened descriptor:** HEARTH (for short statements)

---

## Step 2: Create Products in Stripe

### Architect License ($19/mo)

1. Go to **Products** → **+ Add product**
2. Configure:
   - **Name:** Hearth Writer Architect License
   - **Description:** Commercial license with Shadow Nodes, Visual Tagging, and Multi-LORA mixing
   - **Pricing:** $19.00 USD / month (recurring)
   - **Billing period:** Monthly
3. Click **Save product**
4. Note the **Price ID** (starts with `price_`)

### Showrunner License ($49/seat)

1. Go to **Products** → **+ Add product**
2. Configure:
   - **Name:** Hearth Writer Showrunner License
   - **Description:** Enterprise license with Team Sync, White Labeling, and Legal Indemnity
   - **Pricing:** $49.00 USD / month (recurring, per seat)
   - **Billing period:** Monthly
3. Click **Save product**
4. Note the **Price ID**

---

## Step 3: Create Payment Links (No-Code)

Payment Links are the core of the "Unmanned" system - no server required.

### Architect Payment Link

1. Go to **Payment links** → **+ New**
2. Select **Hearth Writer Architect License**
3. Configure checkout:
   - **Collect email:** Yes (required for key delivery)
   - **Collect phone:** No
   - **Collect billing address:** Yes (for tax compliance)
   - **Allow promotion codes:** Optional
4. **After payment:**
   - **Confirmation page:** Custom URL → `https://yourdomain.com/welcome_architect.html`
   - Or use **Don't show confirmation page** and rely on email
5. Click **Create link**
6. Copy the payment link URL (e.g., `https://buy.stripe.com/xxx`)

### Showrunner Payment Link

1. Go to **Payment links** → **+ New**
2. Select **Hearth Writer Showrunner License**
3. Configure checkout:
   - **Collect email:** Yes
   - **Collect billing address:** Yes
   - **Quantity adjustable:** Yes (for multiple seats)
4. **After payment:**
   - **Confirmation page:** Custom URL → `https://yourdomain.com/welcome_showrunner.html`
5. Click **Create link**
6. Copy the payment link URL

---

## Step 4: Configure Confirmation Pages

The confirmation pages (`welcome_architect.html` and `welcome_showrunner.html`) are already created in the `frontend/public/` directory.

### How They Work

1. After successful payment, Stripe redirects to your confirmation page
2. The page displays a **pre-generated license key** (static for v1.0)
3. Customer copies the key and activates Hearth Writer

### Security Note (v1.0 - Simple)

In v1.0, the confirmation pages contain static placeholder keys. This is acceptable for launch because:
- The pages are "hidden" (not linked from main site)
- Only paying customers receive the redirect URL
- Low volume doesn't justify complex infrastructure

### Upgrade Path (v2.0 - Automated)

For automated key generation:

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Stripe    │────▶│   Webhook   │────▶│  Key Gen    │
│   Payment   │     │   Handler   │     │   Service   │
└─────────────┘     └─────────────┘     └─────────────┘
                           │
                           ▼
                    ┌─────────────┐
                    │   Email     │
                    │   Delivery  │
                    └─────────────┘
```

---

## Step 5: Update Landing Page

Replace the placeholder links in `frontend/public/index.html`:

```html
<!-- Architect Button -->
<a href="https://buy.stripe.com/YOUR_ARCHITECT_LINK" target="_blank" class="btn gold">
    PURCHASE KEY
</a>

<!-- Showrunner Button -->
<a href="https://buy.stripe.com/YOUR_SHOWRUNNER_LINK" target="_blank" class="btn">
    CONTACT SALES
</a>
```

Or for Showrunner, keep as contact form if you prefer manual enterprise sales.

---

## Step 6: License Key Format

### Key Structure

```
HRTH_[TIER]_[RANDOM_ID]

Examples:
- HRTH_ARCHITECT_7x9K2mPq4R
- HRTH_SHOWRUNNER_Ent5Bz8Lw3
```

### Generating Keys (Manual for v1.0)

```bash
# Generate a random Architect key
echo "HRTH_ARCHITECT_$(openssl rand -base64 8 | tr -dc 'a-zA-Z0-9' | head -c 10)"

# Generate a random Showrunner key
echo "HRTH_SHOWRUNNER_$(openssl rand -base64 8 | tr -dc 'a-zA-Z0-9' | head -c 10)"
```

### Key Validation (In App)

The `app.py` validates keys by prefix:

```python
def get_license_tier() -> str:
    key = os.environ.get("HEARTH_LICENSE_KEY", "")
    
    if key.startswith("HRTH_SHOWRUNNER_"):
        return "showrunner"
    if key.startswith("HRTH_ARCHITECT_"):
        return "architect"
    
    return "ronin"  # Free tier
```

---

## Step 7: Testing the Flow

### Test Mode

1. Enable **Test mode** in Stripe Dashboard (toggle in top-right)
2. Create test Payment Links
3. Use test card: `4242 4242 4242 4242` (any future date, any CVC)
4. Verify redirect to confirmation page
5. Verify key display

### Go Live Checklist

- [ ] Sub-account created with "HEARTH WRITER" descriptor
- [ ] Products created (Architect, Showrunner)
- [ ] Payment Links created and tested
- [ ] Confirmation pages deployed
- [ ] Landing page updated with live Payment Link URLs
- [ ] Test purchase completed in live mode
- [ ] Verify statement descriptor on test charge

---

## Pricing Summary

| Tier | Price | Billing | Statement Descriptor |
|------|-------|---------|---------------------|
| Ronin | $0 | Free | N/A |
| Architect | $19/mo | Monthly recurring | HEARTH WRITER |
| Showrunner | $49/seat/mo | Monthly recurring | HEARTH WRITER |

---

## Troubleshooting

### "Statement descriptor invalid"

- Max 22 characters
- No special characters except `.` `-` `'`
- Must be recognizable to customer

### Customer doesn't receive redirect

- Check Payment Link settings → After payment → Confirmation page
- Ensure URL is correct and accessible

### Chargeback received

- Verify statement descriptor is set correctly
- Ensure product description is clear
- Consider adding receipt email with product details

---

## Support

- **Stripe Documentation:** https://stripe.com/docs/payment-links
- **Hearth Writer Issues:** https://github.com/brian95240/hearth-writer/issues

---

*Unmanned. Automated. Professional.*
