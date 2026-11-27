"""Copy for the three country landing pages. Facts are limited to what the site already states
(proof numbers on /pricing and the cold email pages) and to the published law guides."""

ICONS = {
    'mail': '<path d="M4 6h16v12H4z"/><path d="M4 7l8 6 8-6"/>',
    'users': '<circle cx="9" cy="8" r="3.2"/><path d="M3.5 19c.6-3.2 2.8-5 5.5-5s4.9 1.8 5.5 5"/><circle cx="17" cy="9" r="2.4"/><path d="M15.8 14.2c2.3.2 4 1.8 4.7 4.8"/>',
    'server': '<rect x="4" y="4" width="16" height="6.5" rx="1.5"/><rect x="4" y="13.5" width="16" height="6.5" rx="1.5"/><path d="M8 7.2h.01M8 16.7h.01"/>',
    'calendar': '<rect x="4" y="5.5" width="16" height="14.5" rx="2"/><path d="M4 10h16M8.5 3.5v4M15.5 3.5v4"/><path d="M9 14.5l2 2 4-4"/>',
    'crm': '<ellipse cx="12" cy="6" rx="7" ry="2.6"/><path d="M5 6v6c0 1.4 3.1 2.6 7 2.6s7-1.2 7-2.6V6"/><path d="M5 12v6c0 1.4 3.1 2.6 7 2.6s7-1.2 7-2.6v-6"/>',
    'chart': '<path d="M4 20h16"/><path d="M7 16v-4M12 16V8M17 16v-7"/>',
    'phone': '<path d="M6.5 4h3l1.5 4-2 1.3a10 10 0 0 0 5.7 5.7L16 13l4 1.5v3A2 2 0 0 1 17.8 19.5 15.5 15.5 0 0 1 4.5 6.2 2 2 0 0 1 6.5 4z"/>',
}

STATS = [('500+', 'Projects delivered'), ('10M+', 'Cold emails sent'), ('10K+', 'Meetings booked'), ('4.9/5', 'Client rating')]

PROOF = [
    ('500+', 'projects delivered for clients in 30+ countries since 2019'),
    ('100+', 'active clients on month-to-month plans'),
    ('95%+', 'client retention'),
    ('10M+', 'cold emails sent for clients'),
    ('10K+', 'meetings booked for clients'),
    ('4.9/5', 'average client rating'),
]

COMMON_FAQ_DOMAIN = ('Will cold email hurt our main company domain?',
    'No. Campaigns send from separate domains bought and set up only for outreach, each with SPF, DKIM and DMARC, '
    'so the reputation of your main domain and your day-to-day email is kept apart from prospecting.')

PAGES = {}

# ------------------------------------------------------------------ UNITED KINGDOM
PAGES['uk'] = dict(
    slug='lead-generation-agency-uk',
    crumb='United Kingdom',
    country='United Kingdom',
    title='Lead Generation Agency UK for B2B Companies | imisofts',
    description='B2B lead generation for UK companies: verified decision-maker lists, PECR-aware cold email and qualified meetings booked into your calendar. Free audit in 24 hours.',
    badge='Lead generation agency for the UK',
    h1='B2B lead generation for UK companies that fills your calendar with <span>qualified meetings</span>',
    lead=('We find the decision-makers you want to reach across the UK, write to them from properly authenticated inboxes, '
          'and book the interested ones straight into your calendar. Every campaign is set up for PECR and UK GDPR before the first email goes out.'),
    card_title='What a UK campaign includes',
    card_items=[
        'Verified lists of UK decision-makers by sector, region and company size',
        'Separate sending domains and inboxes with SPF, DKIM and DMARC, so your main domain stays protected',
        'Copy written for British buyers, sent during UK working hours',
        'Replies handled and qualified prospects booked into your calendar',
        'A weekly report on emails sent, replies and meetings',
    ],
    card_foot='Month-to-month plans. Sending usually starts about 14 days after kick-off, once the new inboxes are warmed up.',
    services_title='What we run for UK B2B teams',
    services_intro='Outbound that is built, sent and managed for you, from the first list to the meeting in your calendar.',
    services=[
        ('mail', 'Cold email campaigns', 'Short, specific emails written for UK buyers and sent in small daily volumes from warmed inboxes, so they land in the inbox rather than spam.', '/cold-email-marketing', 'Cold email marketing'),
        ('users', 'Decision-maker lists', 'Prospects at UK companies chosen by job title, sector, headcount and region, with every address verified before it enters a campaign.', '/lead-generation', 'B2B lead generation'),
        ('server', 'Sending infrastructure', 'Domains, Google Workspace or Microsoft 365 inboxes, authentication records and warm-up, managed so deliverability stays healthy.', '/email-infrastructure', 'Email infrastructure'),
        ('calendar', 'Appointment setting', 'Replies are answered quickly, questions handled and qualified prospects booked into your calendar with the context of the conversation.', '/lead-generation', 'Appointment setting'),
        ('crm', 'CRM handover', 'Leads and meetings land in HubSpot, Salesforce or your own CRM, so your sales team picks up every conversation where it left off.', '/crm-development', 'CRM development'),
        ('chart', 'Reporting you can act on', 'A weekly view of emails sent, replies, positive replies and meetings by campaign, so you can see which message and audience works.', '/case-studies', 'See client results'),
    ],
    rules_title='Set up for PECR and UK GDPR',
    rules_prose=[
        'Cold email to businesses is allowed in the UK, with conditions. The Privacy and Electronic Communications Regulations (PECR) separate corporate subscribers, such as limited companies and LLPs, from individual subscribers, such as sole traders, and UK GDPR still applies to a named work email address.',
        'We build those conditions into the campaign itself rather than leaving them to the copywriter, and we keep a record of where every contact came from.',
    ],
    rules=[
        ('Corporate addresses only', 'PECR lets you email staff at limited companies, LLPs and public bodies without prior consent. Sole traders and some partnerships count as individuals, so they are left out unless they have opted in.'),
        ('Clear sender and a working opt-out', 'Every email says who it is from and gives a simple way to opt out, and every opt-out is suppressed across all of your campaigns.'),
        ('UK GDPR paperwork', 'A legitimate interests assessment and a privacy notice for the prospect data, because a named work email is personal data.'),
        ('Calls, if you add them', 'Numbers are screened against the TPS and CTPS before anyone is called.'),
    ],
    guides=[('/blog/cold-email-laws-united-kingdom/', 'Cold email laws in the UK'), ('/blog/cold-calling-laws-uk/', 'Cold calling laws in the UK'),
            ('/blog/gdpr-cold-email-compliance/', 'GDPR and cold email'), ('/blog/cold-email-uk-b2b-strategy/', 'UK B2B cold email strategy')],
    steps=[
        ('Free audit and ICP call', 'We look at your offer, your current outbound and your target accounts, and send back a written audit within 24 hours.'),
        ('Infrastructure and lists', 'New sending domains and inboxes are set up and warmed while we build and verify your UK prospect list.'),
        ('Copy and compliance check', 'We write the sequences, agree them with you and check each campaign against PECR and UK GDPR before launch.'),
        ('Launch and booked meetings', 'Campaigns go live, replies are handled and qualified meetings land in your calendar, with a weekly report.'),
    ],
    timezone=('<strong>Time zones that work.</strong> Our team works from Dubai, three to four hours ahead of London depending on the season, '
              'so our working day overlaps with the UK morning and early afternoon and campaigns are checked before your day starts.'),
    faq=[
        ('Is cold email legal in the UK?',
         'Yes, for B2B outreach to corporate addresses, as long as each email identifies the sender, offers a simple way to opt out and the data is handled under UK GDPR. Sole traders and some partnerships are treated as individuals and need consent first. Our <a href="/blog/cold-email-laws-united-kingdom/">UK cold email law guide</a> covers the detail. This is practical guidance, not legal advice.'),
        ('How much does B2B lead generation cost in the UK?',
         'Our plans are month-to-month and priced in US dollars, and the packages are published on our <a href="/pricing">pricing page</a> and the <a href="/cold-email-marketing#packages">cold email packages</a>. The right plan depends on how many inboxes and new contacts a month you need, and the free audit gives you a recommendation before you commit.'),
        ('Can you run UK campaigns from Dubai?',
         'Yes. Outbound is remote work by nature: lists, inboxes, copy and replies are all run online. Emails are scheduled for UK working hours, and we meet on video calls at a time that suits you.'),
        ('Which UK companies is this a good fit for?',
         'B2B companies whose buyers can be identified by job title and company, such as SaaS, agencies, consultancies, recruitment firms, IT and managed service providers and professional services. If you sell mainly to consumers, cold email is the wrong channel under PECR.'),
        COMMON_FAQ_DOMAIN,
        ('How soon will we see meetings?',
         'New inboxes need time to warm up, so sending usually starts about 14 days after kick-off. How quickly meetings follow depends on your market, your offer and the size of your list, and the free audit gives you an honest estimate for your case.'),
    ],
    related=[('/lead-generation-agency-australia', 'Lead generation in Australia', 'Spam Act compliant outbound'),
             ('/lead-generation-dubai', 'Lead generation in Dubai and the UAE', 'From our Business Bay office'),
             ('/blog/cold-email-laws-by-country/', 'Cold email laws by country', 'Rules for 40+ countries')],
    area={'@type': 'Country', 'name': 'United Kingdom'},
    service_name='B2B lead generation in the United Kingdom',
)

# ------------------------------------------------------------------ AUSTRALIA
PAGES['au'] = dict(
    slug='lead-generation-agency-australia',
    crumb='Australia',
    country='Australia',
    title='Lead Generation Agency Australia for B2B Teams | imisofts',
    description='B2B lead generation for Australian companies: verified decision-maker lists, Spam Act compliant cold email and qualified meetings booked for you. Free audit in 24 hours.',
    badge='B2B lead generation for Australia',
    h1='B2B lead generation for Australian companies, with <span>meetings booked</span> for your sales team',
    lead=('We build lists of the decision-makers you want in Sydney, Melbourne, Brisbane, Perth and beyond, reach them with cold email that meets the Spam Act, '
          'and book the interested ones into your calendar. You get the meetings without hiring and managing an SDR team.'),
    card_title='What an Australian campaign includes',
    card_items=[
        'Verified lists of Australian decision-makers by industry, state and company size',
        'Separate sending domains and inboxes with SPF, DKIM and DMARC, so your main domain stays protected',
        'Emails scheduled to arrive in business hours in each state\'s time zone',
        'Replies handled and qualified prospects booked into your calendar',
        'A weekly report on emails sent, replies and meetings',
    ],
    card_foot='Month-to-month plans. Sending usually starts about 14 days after kick-off, once the new inboxes are warmed up.',
    services_title='What we run for Australian B2B teams',
    services_intro='Done-for-you outbound, from the first list to the meeting in your calendar, set up around Australian rules and time zones.',
    services=[
        ('mail', 'Cold email campaigns', 'Plain, relevant emails written for Australian buyers and sent in small daily volumes from warmed inboxes, so they reach the inbox.', '/cold-email-marketing', 'Cold email marketing'),
        ('users', 'Decision-maker lists', 'Prospects chosen by job title, industry, headcount, state and city, with every address verified before it enters a campaign.', '/lead-generation', 'B2B lead generation'),
        ('server', 'Sending infrastructure', 'Domains, Google Workspace or Microsoft 365 inboxes, authentication records and warm-up, managed so deliverability stays healthy.', '/email-infrastructure', 'Email infrastructure'),
        ('calendar', 'Appointment setting', 'Replies are answered quickly, questions handled and qualified prospects booked into your calendar with the context of the conversation.', '/lead-generation', 'Appointment setting'),
        ('phone', 'AI voice follow-up', 'Optional AI voice agents for inbound calls and follow-ups, kept to the rules on calling hours and the Do Not Call Register.', '/ai-voice-agents', 'AI voice agents'),
        ('chart', 'Reporting you can act on', 'A weekly view of emails sent, replies, positive replies and meetings by campaign, so you can see which message and audience works.', '/case-studies', 'See client results'),
    ],
    rules_title='Built around the Spam Act 2003',
    rules_prose=[
        'Australia\'s Spam Act needs consent for commercial email, and the ACMA enforces it. For B2B outreach, consent can be inferred when a work address is conspicuously published and the message is relevant to the person\'s role.',
        'We only email contacts who meet that test, and every message carries the sender details and unsubscribe the Act requires.',
    ],
    rules=[
        ('Inferred consent, checked', 'Contacts are included only where their work address is published, there is no statement refusing marketing, and the email relates to their job.'),
        ('Sender details in every email', 'Each message clearly identifies the business sending it and how to contact that business.'),
        ('A working unsubscribe', 'Every email has a functional unsubscribe, and requests are actioned well inside the five working days the Act allows.'),
        ('Calls, if you add them', 'Numbers are checked against the Do Not Call Register where it applies, and calls stay inside the permitted calling hours.'),
    ],
    guides=[('/blog/cold-email-laws-australia/', 'Cold email laws in Australia'), ('/blog/cold-calling-laws-australia/', 'Cold calling laws in Australia'),
            ('/blog/cold-email-laws-by-country/', 'Cold email laws by country')],
    steps=[
        ('Free audit and ICP call', 'We look at your offer, your current outbound and your target accounts, and send back a written audit within 24 hours.'),
        ('Infrastructure and lists', 'New sending domains and inboxes are set up and warmed while we build and verify your Australian prospect list.'),
        ('Copy and compliance check', 'We write the sequences, agree them with you and check every campaign against the Spam Act before launch.'),
        ('Launch and booked meetings', 'Campaigns go live, replies are handled and qualified meetings land in your calendar, with a weekly report.'),
    ],
    timezone=('<strong>Time zones that work.</strong> Our team works from Dubai, six to seven hours behind Sydney depending on daylight saving. '
              'Emails are scheduled to arrive in Australian business hours, and our working day starts in your afternoon, so replies are handled the same day.'),
    faq=[
        ('Is cold email legal in Australia?',
         'Yes, with consent. For B2B outreach, consent can be inferred when a work email address is conspicuously published, there is no statement saying the person does not want marketing, and the message is relevant to their role. Every email must identify the sender and include a working unsubscribe. Our <a href="/blog/cold-email-laws-australia/">Australian cold email law guide</a> explains it in full. This is practical guidance, not legal advice.'),
        ('How much does B2B lead generation cost in Australia?',
         'Our plans are month-to-month and priced in US dollars, and the packages are published on our <a href="/pricing">pricing page</a> and the <a href="/cold-email-marketing#packages">cold email packages</a>. The right plan depends on how many inboxes and new contacts a month you need, and the free audit gives you a recommendation before you commit.'),
        ('Do you cover the whole of Australia?',
         'Yes. Lists can target any state or city, from Sydney, Melbourne and Brisbane to Perth, Adelaide and regional areas, and sending is scheduled for the recipient\'s own time zone.'),
        ('Which Australian companies is this a good fit for?',
         'B2B companies whose buyers can be identified by job title and company, such as SaaS, agencies, consultancies, recruitment firms, IT and managed service providers and professional services.'),
        COMMON_FAQ_DOMAIN,
        ('How soon will we see meetings?',
         'New inboxes need time to warm up, so sending usually starts about 14 days after kick-off. How quickly meetings follow depends on your market, your offer and the size of your list, and the free audit gives you an honest estimate for your case.'),
    ],
    related=[('/lead-generation-agency-uk', 'Lead generation in the UK', 'PECR and UK GDPR ready'),
             ('/lead-generation-dubai', 'Lead generation in Dubai and the UAE', 'From our Business Bay office'),
             ('/blog/cold-email-laws-by-country/', 'Cold email laws by country', 'Rules for 40+ countries')],
    area={'@type': 'Country', 'name': 'Australia'},
    service_name='B2B lead generation in Australia',
)

# ------------------------------------------------------------------ DUBAI / UAE
PAGES['ae'] = dict(
    slug='lead-generation-dubai',
    crumb='Dubai and the UAE',
    country='United Arab Emirates',
    title='Lead Generation Company in Dubai for B2B Teams | imisofts',
    description='Dubai-based B2B lead generation: verified decision-maker lists across the UAE and GCC, compliant cold email and qualified meetings booked into your calendar. Free audit in 24 hours.',
    badge='Based in Business Bay, Dubai',
    h1='Lead generation company in Dubai that books <span>qualified B2B meetings</span>',
    lead=('We find the decision-makers you want to reach in Dubai, Abu Dhabi and across the GCC, contact them through cold email that follows UAE rules, '
          'and book the interested ones into your calendar. Campaigns run on the UAE working week, Monday to Friday.'),
    card_title='What a UAE campaign includes',
    card_items=[
        'Verified lists of decision-makers at UAE and GCC companies by sector, emirate and company size',
        'Separate sending domains and inboxes with SPF, DKIM and DMARC, so your main domain stays protected',
        'Copy written for Gulf buyers, sent in Gulf business hours',
        'Replies handled and qualified prospects booked into your calendar',
        'A weekly report on emails sent, replies and meetings',
    ],
    card_foot='Month-to-month plans. Sending usually starts about 14 days after kick-off, once the new inboxes are warmed up.',
    services_title='What we run for B2B teams in the UAE',
    services_intro='Done-for-you outbound from a Dubai team, from the first list to the meeting in your calendar.',
    services=[
        ('mail', 'Cold email campaigns', 'Short, specific emails written for decision-makers in the Gulf and sent in small daily volumes from warmed inboxes.', '/cold-email-marketing', 'Cold email marketing'),
        ('users', 'Decision-maker lists', 'Prospects in Dubai, Abu Dhabi, Sharjah and the wider GCC by job title, sector and company size, verified before they enter a campaign.', '/lead-generation', 'B2B lead generation'),
        ('server', 'Sending infrastructure', 'Domains, Google Workspace or Microsoft 365 inboxes, authentication records and warm-up, managed so deliverability stays healthy.', '/email-infrastructure', 'Email infrastructure'),
        ('calendar', 'Appointment setting', 'Replies are answered quickly, questions handled and qualified prospects booked into your calendar with the context of the conversation.', '/lead-generation', 'Appointment setting'),
        ('phone', 'Calls and AI voice agents', 'Calling by your team or an AI voice agent, kept inside the UAE telemarketing rules on hours, caller numbers and the Do Not Call Registry.', '/ai-voice-agents', 'AI voice agents'),
        ('crm', 'CRM and GoHighLevel', 'Leads and meetings land in HubSpot, GoHighLevel or your own CRM, so your team picks up every conversation where it left off.', '/gohighlevel-services', 'GoHighLevel services'),
    ],
    rules_title='Built for UAE rules',
    rules_prose=[
        'B2B lead generation in the UAE runs on email, LinkedIn, calls and WhatsApp, and three of those come with their own rulebook. Named contacts are personal data under the federal data protection law, and telemarketing has been tightly regulated since 2024.',
        'We build those rules into every campaign, and we keep a record of where each contact came from.',
    ],
    rules=[
        ('Work addresses and a data record', 'Email to a named person is personal data under Federal Decree-Law No. 45 of 2021, and companies in DIFC and ADGM have their own data protection rules, so we use business addresses only and log each contact\'s source.'),
        ('Clear sender and a working opt-out', 'Every email names the sender and offers a simple way to opt out, honoured across all of your campaigns.'),
        ('Telemarketing rules', 'Calls follow Cabinet Resolution 56 of 2024: 9 a.m. to 6 p.m. only, from numbers on your trade licence, and never to numbers on the Do Not Call Registry.'),
        ('WhatsApp only with opt-in', 'WhatsApp is used only with contacts who have opted in, as WhatsApp\'s business messaging policy requires.'),
    ],
    guides=[('/blog/b2b-lead-generation-uae/', 'B2B lead generation in the UAE'), ('/blog/cold-email-laws-uae/', 'Cold email laws in the UAE'),
            ('/blog/cold-calling-laws-uae/', 'Cold calling laws in the UAE')],
    steps=[
        ('Free audit and ICP call', 'We look at your offer, your current outbound and your target accounts, and send back a written audit within 24 hours.'),
        ('Infrastructure and lists', 'New sending domains and inboxes are set up and warmed while we build and verify your UAE and GCC prospect list.'),
        ('Copy and compliance check', 'We write the sequences, agree them with you and check every campaign against UAE rules before launch.'),
        ('Launch and booked meetings', 'Campaigns go live, replies are handled and qualified meetings land in your calendar, with a weekly report.'),
    ],
    timezone=('<strong>A Dubai team on your hours.</strong> imisofts is headquartered in The Prism Tower, Business Bay, '
              'and campaigns run on Gulf Standard Time and the UAE working week, so replies are handled while your prospects are at their desks.'),
    faq=[
        ('Is cold email legal in the UAE?',
         'B2B cold email to business addresses is widely used in the UAE. Treat named contacts as personal data under the federal data protection law, identify yourself in every email and honour every opt-out. Our <a href="/blog/cold-email-laws-uae/">UAE cold email law guide</a> covers the detail. This is practical guidance, not legal advice.'),
        ('How much does lead generation cost in Dubai?',
         'Our plans are month-to-month and priced in US dollars (the dirham is pegged at about 3.67 to the dollar). The packages are published on our <a href="/pricing">pricing page</a> and the <a href="/cold-email-marketing#packages">cold email packages</a>, and the free audit gives you a recommendation before you commit.'),
        ('Can you run lead generation for Saudi Arabia and the rest of the GCC?',
         'Yes. We build lists and run campaigns across the GCC, including Saudi Arabia, Qatar, Kuwait, Bahrain and Oman, and adapt the setup to each country\'s own data protection and calling rules.'),
        ('Do you offer telemarketing or AI calling in the UAE?',
         'We can add calls to a campaign, by your team or an <a href="/ai-voice-agents">AI voice agent</a>, as long as they follow the UAE rules: 9 a.m. to 6 p.m., from numbers registered to your trade licence, and never to numbers on the Do Not Call Registry.'),
        COMMON_FAQ_DOMAIN,
        ('How soon will we see meetings?',
         'New inboxes need time to warm up, so sending usually starts about 14 days after kick-off. How quickly meetings follow depends on your market, your offer and the size of your list, and the free audit gives you an honest estimate for your case.'),
    ],
    related=[('/lead-generation-agency-uk', 'Lead generation in the UK', 'PECR and UK GDPR ready'),
             ('/lead-generation-agency-australia', 'Lead generation in Australia', 'Spam Act compliant outbound'),
             ('/blog/cold-email-agency-dubai/', 'Cold email agency in Dubai', 'How we serve clients worldwide')],
    area=[{'@type': 'City', 'name': 'Dubai'}, {'@type': 'Country', 'name': 'United Arab Emirates'}],
    service_name='B2B lead generation in Dubai and the UAE',
)
