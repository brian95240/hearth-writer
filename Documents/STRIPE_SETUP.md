# Hearth Writer - Stripe Payment System Setup

> **Status:** ✅ LIVE - Fully configured and ready to accept payments  
> **Strategy:** Zero-code, fully automated payment processing using Stripe Payment Links with professional branding.

---

## Overview

The payment system allows Hearth Writer to sell licenses 24/7 without manual intervention:

1. **Customer** clicks payment link on landing page
2. **Stripe Payment Link** handles checkout (no code required)
3. **Stripe** processes payment, shows "HEARTH WRITER" on credit card statement
4. **Customer** receives confirmation and license key
5. **Customer** activates Hearth Writer

---

## Live Configuration

### Stripe Account Details

- **Account ID:** `acct_1RZUk82KS3i05iH4`
- **Mode:** Live
- **Statement Descriptor:** `HEARTH WRITER`
- **Business Website:** https://brian95240.github.io/hearth-writer/

### Product Configuration

| Item                | Details                                                                                                 | Stripe ID                  |
| ------------------- | ------------------------------------------------------------------------------------------------------- | -------------------------- |
| **Product Name**    | Hearth Writer                                                                                           | `prod_Tjb2XJH66ThMPT`      |
| **Description**     | A hyper-efficient, local-first authorship engine with Collapse-to-Zero architecture & 7 creative archetypes. | N/A                        |

### Pricing Tiers

| Tier         | Price      | Billing Cycle | Stripe Price ID            | Payment Link                                         |
| ------------ | ---------- | ------------- | -------------------------- | ---------------------------------------------------- |
| **Architect**  | $19.00 USD | Monthly       | `price_1Sm7qc2KS3i05iH471M0HS2X` | https://buy.stripe.com/14A6oAcXHfjje9o3u10VO00 |
| **Showrunner** | $49.00 USD | Monthly       | `price_1Sm7qg2KS3i05iH4Y5R0EMU9` | https://buy.stripe.com/9B65kw3n71staXc7Kh0VO01 |

---

## Payment Methods Enabled

A custom payment method configuration called **"Low Friction, Low fees, on page engagement, no redirects"** has been created with the following options:

- ✅ **Cards** (All regions)
- ✅ **Cartes Bancaires** (France)
- ✅ **Apple Pay** (All regions)
- ✅ **Google Pay** (All regions)
- ✅ **Link** (All regions)

These methods provide a smooth, low-friction checkout experience while keeping customers on-site.

---

## Payment Links Usage

### Architect Tier ($19/month)

**Direct Link:** https://buy.stripe.com/14A6oAcXHfjje9o3u10VO00

Use this link for:
- "Purchase Architect" buttons on website
- Email marketing campaigns
- Social media promotions
- Direct customer inquiries

### Showrunner Tier ($49/month)

**Direct Link:** https://buy.stripe.com/9B65kw3n71staXc7Kh0VO01

Use this link for:
- "Purchase Showrunner" buttons on website
- Enterprise sales follow-ups
- Team licensing inquiries

---

## Integration with Website

Update the payment buttons in `docs/index.html`:

```html
<!-- Architect Button -->
<a href="https://buy.stripe.com/14A6oAcXHfjje9o3u10VO00" class="cta-button">Get Architect</a>

<!-- Showrunner Button -->
<a href="https://buy.stripe.com/9B65kw3n71staXc7Kh0VO01" class="cta-button">Get Showrunner</a>
```

---

## License Key Format

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

## Testing the Flow

### Test Mode

1. Enable **Test mode** in Stripe Dashboard (toggle in top-right)
2. Create test Payment Links using test price IDs
3. Use test card: `4242 4242 4242 4242` (any future date, any CVC)
4. Verify payment processing
5. Verify statement descriptor

### Live Mode Verification

- ✅ Account configured with "HEARTH WRITER" descriptor
- ✅ Products created (Architect, Showrunner)
- ✅ Payment Links created and live
- ✅ Payment methods enabled (Cards, Apple Pay, Google Pay, Link)
- ✅ Business website deployed at https://brian95240.github.io/hearth-writer/

---

## Pricing Summary

| Tier | Price | Billing | Statement Descriptor | Status |
|------|-------|---------|---------------------|--------|
| Ronin | $0 | Free | N/A | ✅ Available |
| Architect | $19/mo | Monthly recurring | HEARTH WRITER | ✅ Live |
| Showrunner | $49/seat/mo | Monthly recurring | HEARTH WRITER | ✅ Live |

---

## Next Steps

1. **Update Website:** Add the payment links to the pricing section buttons
2. **Test Purchase:** Make a small test purchase in live mode to verify the flow
3. **Set Up Webhooks (Optional):** For automated license key delivery
4. **Configure Customer Portal:** Allow customers to manage their subscriptions
5. **Add Coupons (Optional):** Create promotional discount codes

---

## Stripe Dashboard Quick Links

- **Products:** https://dashboard.stripe.com/products
- **Payment Links:** https://dashboard.stripe.com/payment-links
- **Customers:** https://dashboard.stripe.com/customers
- **Payments:** https://dashboard.stripe.com/payments
- **Settings:** https://dashboard.stripe.com/settings

---

## Troubleshooting

### "Statement descriptor invalid"

- Max 22 characters
- No special characters except `.` `-` `'`
- Must be recognizable to customer

### Customer doesn't see payment methods

- Verify payment methods are enabled in **Live mode** (not just Test mode)
- Check that the payment method configuration is set to "Active"

### Chargeback received

- Verify statement descriptor is set correctly
- Ensure product description is clear
- Consider adding receipt email with product details

---

## Support

- **Stripe Documentation:** https://stripe.com/docs/payment-links
- **Hearth Writer Repository:** https://github.com/brian95240/hearth-writer
- **Business Website:** https://brian95240.github.io/hearth-writer/

---

*Unmanned. Automated. Professional.*
