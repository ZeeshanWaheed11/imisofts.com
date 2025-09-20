# SPP.co Setup Guide for imisofts

## Initial Login
1. Go to https://spp.co/login
2. Enter your workspace URL (find this in your welcome email)
3. Login with: zeeshan@imisofts.com

## Step 1: Company Settings

### Navigate to: Settings → Company
Fill in:
- **Company Name**: imisofts
- **Support Email**: support@imisofts.com (or zeeshan@imisofts.com)
- **Website**: https://imisofts.com
- **Phone**: [Your phone number]
- **Address**: [Your business address]
- **Timezone**: UAE (GMT+4)

## Step 2: Branding Setup

### Navigate to: Settings → Branding

1. **Upload Logo**:
   - Use your logo from the website
   - Recommended size: 200x50px

2. **Colors**:
   - Primary Color: #F45407 (Orange)
   - Secondary Color: #333333 (Dark Gray)
   - Success Color: #10b981 (Green)
   - Danger Color: #ef4444 (Red)

3. **Custom CSS** (Optional):
```css
.btn-primary {
  background: linear-gradient(135deg, #F45407, #ff6b28);
  border: none;
}
.navbar {
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}
```

## Step 3: Service Catalog Setup

### Navigate to: Billing → Services → Add Service

#### Service 1: Cold Email Infrastructure - Starter
- **Name**: Email Infrastructure - Starter Package
- **Price**: $489
- **Billing**: One-time
- **Description**:
  ```
  Complete email infrastructure setup for cold outreach
  - 10 premium domains
  - 70 professional inboxes
  - Complete DMARC/SPF/DKIM setup
  - 14-day warming protocol
  - Platform integration
  ```
- **Deliverables**:
  - Domain purchase and configuration
  - Email account setup
  - DNS configuration
  - Warming schedule implementation
  - Platform integration guide

#### Service 2: Cold Email Infrastructure - Professional
- **Name**: Email Infrastructure - Professional Package
- **Price**: $1,225
- **Billing**: One-time
- **Description**:
  ```
  Scale your outreach with professional infrastructure
  - 25 premium domains
  - 175 professional inboxes
  - Priority server allocation
  - Advanced IP management
  - Reputation monitoring dashboard
  ```

#### Service 3: Cold Email Infrastructure - Enterprise
- **Name**: Email Infrastructure - Enterprise Package
- **Price**: $2,450
- **Billing**: One-time
- **Description**:
  ```
  Unlimited scaling potential for serious operations
  - 50+ domains scalable
  - 350+ professional inboxes
  - Dedicated server cluster
  - Custom warming schedules
  - 24/7 priority support
  ```

#### Service 4: Cold Email Campaign - Foundation
- **Name**: Campaign Setup - Foundation
- **Price**: $1,899
- **Billing**: One-time
- **Description**:
  ```
  Complete cold email campaign setup
  - Instantly.ai configuration
  - 3 email sequences
  - Basic personalization
  - 5,000 verified leads
  - Campaign optimization
  ```

#### Service 5: Cold Email Campaign - Accelerator
- **Name**: Campaign Setup - Accelerator
- **Price**: $2,999
- **Billing**: One-time
- **Description**:
  ```
  Advanced campaign with AI optimization
  - Everything in Foundation
  - 5 email sequences
  - AI personalization
  - 10,000 verified leads
  - A/B testing setup
  - Weekly optimization
  ```

#### Service 6: Cold Email Campaign - Enterprise
- **Name**: Campaign Setup - Enterprise
- **Price**: $4,899
- **Billing**: One-time
- **Description**:
  ```
  Full-scale market domination
  - Unlimited email sequences
  - Advanced AI personalization
  - 25,000 verified leads
  - Dedicated campaign manager
  - Daily optimization
  - Custom integrations
  ```

#### Service 7: AI Automation Consulting
- **Name**: AI Automation Implementation
- **Price**: $2,500
- **Billing**: One-time
- **Description**:
  ```
  Custom AI automation for your business processes
  - Process analysis and mapping
  - AI tool selection and setup
  - Workflow automation
  - Team training
  - 30-day support
  ```

#### Service 8: CRM Development
- **Name**: Custom CRM Development
- **Price**: $5,000
- **Billing**: Project-based
- **Description**:
  ```
  Tailored CRM solution for your business
  - Requirements analysis
  - Custom development
  - Integration with existing tools
  - Data migration
  - Training and documentation
  ```

#### Service 9: Shopify App Development
- **Name**: Custom Shopify App
- **Price**: $3,500
- **Billing**: One-time
- **Description**:
  ```
  Custom Shopify app development
  - App design and development
  - Shopify API integration
  - Testing and deployment
  - App store submission
  - 60-day support
  ```

#### Service 10: Web Development
- **Name**: Professional Website Development
- **Price**: $2,000
- **Billing**: Starting price
- **Description**:
  ```
  Modern, responsive website development
  - Custom design
  - Mobile responsive
  - SEO optimized
  - CMS integration
  - 3 months support
  ```

## Step 4: Order Forms

### Navigate to: Billing → Order Forms → Create

#### Form 1: Email Infrastructure Order
- **Name**: Email Infrastructure Packages
- **URL Slug**: email-infrastructure
- **Services**: Add all 3 infrastructure packages
- **Fields**:
  - Company Name (Required)
  - Website URL (Required)
  - Current Email Volume (Dropdown)
  - Preferred Start Date
  - Additional Notes

#### Form 2: Campaign Setup Order
- **Name**: Cold Email Campaign Setup
- **URL Slug**: campaign-setup
- **Services**: Add all 3 campaign packages
- **Fields**:
  - Company Name
  - Target Market
  - Product/Service Description
  - Target Contact Titles
  - Geographic Focus
  - Campaign Goals

## Step 5: Payment Configuration

### Navigate to: Billing → Payment Methods

#### Option A: Stripe Setup (Recommended)
1. Click "Connect Stripe"
2. Follow Stripe onboarding
3. Enable test mode first
4. Test with card: 4242 4242 4242 4242

#### Option B: Manual Payments (for Ziina)
1. Add Payment Method → Manual
2. **Name**: Ziina Transfer
3. **Instructions**:
   ```
   Please complete payment using the secure link sent to your email.
   Payment will be confirmed within 24 hours.
   ```
4. **Details**: Include Ziina payment instructions

## Step 6: Email Templates

### Navigate to: Settings → Email Templates

#### Template 1: Welcome Email
**Subject**: Welcome to imisofts - Let's Get Started!
```
Hi {{client.first_name}},

Welcome to imisofts! We're excited to work with you.

Your account has been created and you can access your client portal here:
{{portal.link}}

Your dedicated account manager will reach out within 24 hours to begin your onboarding.

Best regards,
The imisofts Team
```

#### Template 2: Invoice Email
**Subject**: Invoice #{{invoice.number}} from imisofts
```
Hi {{client.first_name}},

Your invoice for {{service.name}} is ready:

Amount: {{invoice.total}}
Due Date: {{invoice.due_date}}

View and pay invoice: {{invoice.link}}

Thank you for your business!

Best regards,
imisofts
```

#### Template 3: Project Update
**Subject**: Project Update: {{project.name}}
```
Hi {{client.first_name}},

Here's your project status update:

Project: {{project.name}}
Status: {{project.status}}
Progress: {{project.progress}}%

View full details in your portal: {{portal.link}}

Best regards,
Your imisofts Team
```

## Step 7: Team Setup

### Navigate to: Team → Add Member

Add your team members:
1. **Name**: [Team Member Name]
2. **Email**: [Email]
3. **Role**: Admin/Support/Developer
4. **Permissions**: Select appropriate permissions

## Step 8: Client Portal Customization

### Navigate to: Settings → Portal

1. **Portal URL**: https://clients.imisofts.com (custom domain)
2. **Welcome Message**:
   ```
   Welcome to your imisofts Client Portal
   Access your projects, invoices, and support all in one place.
   ```
3. **Features to Enable**:
   - ✅ Invoices
   - ✅ Projects
   - ✅ Support Tickets
   - ✅ Files
   - ✅ Messages
   - ✅ Knowledge Base

## Step 9: Integrations

### Navigate to: Settings → Integrations

1. **Slack**: Connect for team notifications
2. **Google Drive**: For file storage
3. **Zapier**: For automation
4. **Calendar**: For scheduling

## Step 10: Testing

### Create Test Client
1. Go to Clients → Add Client
2. **Name**: Test Client
3. **Email**: test@example.com
4. **Company**: Test Company

### Create Test Invoice
1. Go to Billing → Invoices → Create
2. Select Test Client
3. Add Service: Email Infrastructure - Starter
4. Send test invoice

### Test Client Portal
1. Use incognito browser
2. Access portal link from email
3. Verify all features work

## Step 11: Automation Setup

### Navigate to: Automations → Create

#### Automation 1: New Client Welcome
- **Trigger**: New client created
- **Actions**:
  - Send welcome email
  - Create onboarding project
  - Notify team in Slack

#### Automation 2: Invoice Reminder
- **Trigger**: Invoice due in 3 days
- **Actions**:
  - Send reminder email
  - Update invoice status
  - Notify account manager

#### Automation 3: Project Completion
- **Trigger**: Project marked complete
- **Actions**:
  - Send completion email
  - Request feedback
  - Generate final invoice

## Step 12: Knowledge Base

### Navigate to: Support → Knowledge Base

Create articles for:
1. How to access your client portal
2. How to view and pay invoices
3. How to submit support tickets
4. Project delivery timeline
5. Frequently asked questions

## Step 13: Final Configuration

### Security Settings
1. Enable 2FA for your account
2. Set password requirements
3. Configure session timeout
4. Set up IP whitelist (optional)

### Notification Settings
1. Configure email notifications
2. Set up Slack alerts
3. Enable SMS notifications (optional)

### Backup Settings
1. Enable automatic backups
2. Set backup frequency
3. Configure backup retention

## Step 14: Go Live Checklist

- [ ] All services added with correct pricing
- [ ] Order forms created and tested
- [ ] Payment methods configured
- [ ] Email templates customized
- [ ] Team members added
- [ ] Client portal branded
- [ ] Test client and invoice created
- [ ] Automations configured
- [ ] Knowledge base populated
- [ ] Security settings configured

## Post-Setup Tasks

1. **Change Password**: Update to a secure password only you know
2. **Document Access**: Save all important URLs and access details
3. **Team Training**: Schedule training for team members
4. **Client Migration**: Import existing clients
5. **Launch Announcement**: Notify clients about new portal

## Support Resources

- SPP.co Documentation: https://help.spp.co
- Video Tutorials: Check SPP.co dashboard
- Support: support@spp.co
- Community: SPP.co Slack community

## Custom Ziina Integration

Since Ziina isn't natively supported, here's the workaround:

1. **Manual Process**:
   - Generate invoice in SPP.co
   - Create Ziina payment link
   - Send link via SPP.co messaging
   - Mark invoice paid manually

2. **Semi-Automated** (Using Zapier):
   - New invoice trigger in SPP.co
   - Create payment link via Ziina API
   - Email link to customer
   - Update invoice status

3. **Webhook Setup** (Advanced):
   - Create webhook endpoint
   - Listen for SPP.co invoice events
   - Generate Ziina links automatically
   - Update payment status via API

---

## Notes

- Start with manual Ziina process
- Test everything with small amounts first
- Keep this guide updated as you customize
- Regular backups are important
- Monitor usage and upgrade plan as needed

**Remember to change your password after setup is complete!**