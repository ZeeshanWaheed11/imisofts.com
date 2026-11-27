CHECK_SVG = ("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 16 16' fill='none' "
             "stroke='%23F45407' stroke-width='2.4' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M3 8.5l3.2 3L13 4.5'/%3E%3C/svg%3E")

GEO_CSS = """
<style id="geo-landing-1127">
.gl-hero{padding:128px 0 80px;background:linear-gradient(to bottom,#ffffff,#f9fafb)}
.gl-crumbs{font-size:13px;color:#98a2b3;margin-bottom:18px}
.gl-crumbs a{color:#667085;text-decoration:none}
.gl-crumbs a:hover{color:#F45407}
.gl-crumbs span{margin:0 6px}
.gl-hero-grid{display:grid;grid-template-columns:1.1fr .9fr;gap:56px;align-items:center}
.gl-badge{display:inline-flex;align-items:center;padding:6px 12px;background:#fff5f3;border-radius:50px;margin-bottom:24px;color:#F45407;font-size:14px;font-weight:500}
.gl-badge::before{content:'';width:8px;height:8px;background:#F45407;border-radius:50%;margin-right:8px;flex:0 0 8px}
.gl-hero h1{font-size:48px;font-weight:800;line-height:1.2;margin-bottom:24px;color:#1a1a1a}
.gl-hero h1 span{color:#F45407}
.gl-lead{font-size:18px;color:#666;line-height:1.6;margin-bottom:32px}
.gl-ctas{display:flex;gap:16px;margin-bottom:44px;flex-wrap:wrap}
.gl-btn{display:inline-block;padding:12px 24px;border-radius:8px;font-weight:500;text-decoration:none;font-size:16px;transition:background-color .2s ease,border-color .2s ease,transform .2s ease}
.gl-btn-primary{background:#F45407;color:#fff}
.gl-btn-primary:hover{background:#d94a06;transform:translateY(-1px)}
.gl-btn-secondary{background:#fff;color:#333;border:1px solid #e5e5e5}
.gl-btn-secondary:hover{border-color:#F45407;color:#F45407}
.gl-stats{display:grid;grid-template-columns:repeat(4,1fr);gap:24px}
.gl-stat-num{font-size:24px;font-weight:500;color:#1a1a1a}
.gl-stat-label{font-size:14px;color:#999;line-height:1.4}
.gl-card{background:#fff;border-radius:16px;padding:28px;box-shadow:0 20px 40px rgba(0,0,0,.1);border:1px solid #f0f0f0}
.gl-card-title{font-size:12px;text-transform:uppercase;letter-spacing:1px;color:#999;margin-bottom:20px}
.gl-check{list-style:none;margin:0;padding:0;display:flex;flex-direction:column;gap:14px}
.gl-check li{display:flex;gap:12px;font-size:15px;color:#444;line-height:1.55}
.gl-check li::before{content:'';flex:0 0 22px;height:22px;border-radius:50%;background:#fff5f3 url("CHECK") center/12px no-repeat;margin-top:1px}
.gl-card-foot{margin-top:22px;padding-top:18px;border-top:1px solid #f0f0f0;font-size:13px;color:#999;line-height:1.5}
.gl-section{padding:88px 0}
.gl-alt{background:#f9fafb}
.gl-head{max-width:780px;margin:0 auto 48px;text-align:center}
.gl-eyebrow{display:inline-block;color:#F45407;font-size:13px;font-weight:600;letter-spacing:1px;text-transform:uppercase;margin-bottom:12px}
.gl-section h2,.gl-contact h2{font-size:36px;font-weight:700;color:#0F172A;line-height:1.25;margin-bottom:16px}
.gl-head p{font-size:17px;color:#666;line-height:1.7}
.gl-grid3{display:grid;grid-template-columns:repeat(3,1fr);gap:24px}
.gl-tile{background:#fff;border:1px solid #eef0f3;border-radius:14px;padding:28px;transition:border-color .2s ease,box-shadow .2s ease,transform .2s ease}
.gl-tile:hover{border-color:rgba(244,84,7,.35);box-shadow:0 12px 28px rgba(15,23,42,.06);transform:translateY(-2px)}
.gl-icon{width:44px;height:44px;border-radius:10px;background:#fff5f3;color:#F45407;display:flex;align-items:center;justify-content:center;margin-bottom:18px}
.gl-tile h3,.gl-step h3{font-size:18px;font-weight:600;color:#0F172A;margin-bottom:10px;line-height:1.35}
.gl-tile p,.gl-step p{font-size:15px;color:#555;line-height:1.65}
.gl-tile p{margin-bottom:14px}
.gl-more{color:#F45407;font-weight:500;text-decoration:none;font-size:14px}
.gl-more:hover{text-decoration:underline}
.gl-split{display:grid;grid-template-columns:.95fr 1.05fr;gap:56px;align-items:start}
.gl-prose p{font-size:17px;color:#475569;line-height:1.8;margin-bottom:18px}
.gl-prose a{color:#F45407}
.gl-rules{display:flex;flex-direction:column;gap:14px}
.gl-rule{background:#fff;border:1px solid #eef0f3;border-left:3px solid #F45407;border-radius:12px;padding:20px 22px}
.gl-rule strong{display:block;color:#0F172A;font-size:16px;margin-bottom:6px;font-weight:600}
.gl-rule p{font-size:15px;color:#555;line-height:1.65;margin:0}
.gl-pills{display:flex;flex-wrap:wrap;gap:10px;margin:6px 0 4px}
.gl-pills a{font-size:14px;padding:8px 14px;border-radius:50px;border:1px solid #e5e7eb;color:#333;text-decoration:none;background:#fff;transition:border-color .2s ease,color .2s ease}
.gl-pills a:hover{border-color:#F45407;color:#F45407}
.gl-note,.gl-prose .gl-note{font-size:13px;color:#888;margin-top:16px;line-height:1.6}
.gl-steps{display:grid;grid-template-columns:repeat(4,1fr);gap:24px;counter-reset:glstep}
.gl-step{padding:28px 24px;border-radius:14px;background:#fff;border:1px solid #eef0f3}
.gl-step::before{counter-increment:glstep;content:counter(glstep,decimal-leading-zero);font-size:13px;font-weight:700;color:#F45407;letter-spacing:1px;display:block;margin-bottom:12px}
.gl-proof{display:grid;grid-template-columns:repeat(3,1fr);gap:20px}
.gl-proof-item{background:#fff;border-radius:14px;padding:26px;border:1px solid #eef0f3}
.gl-proof-num{font-size:30px;font-weight:800;color:#F45407;margin-bottom:6px;line-height:1.1}
.gl-proof-label{font-size:15px;color:#555;line-height:1.5}
.gl-band{margin-top:32px;background:#0F172A;color:#e2e8f0;border-radius:16px;padding:28px 32px;display:flex;gap:24px;align-items:center;justify-content:space-between;flex-wrap:wrap}
.gl-band p{font-size:16px;line-height:1.65;margin:0;max-width:760px}
.gl-band strong{color:#fff}
.gl-faq{max-width:860px;margin:0 auto;display:flex;flex-direction:column;gap:12px}
.gl-faq details{background:#fff;border:1px solid #eef0f3;border-radius:12px;padding:20px 24px}
.gl-faq summary{cursor:pointer;font-weight:600;font-size:17px;color:#0F172A;list-style:none;display:flex;justify-content:space-between;align-items:flex-start;gap:16px;line-height:1.45}
.gl-faq summary::-webkit-details-marker{display:none}
.gl-faq summary::after{content:'+';color:#F45407;font-size:22px;line-height:1;flex:0 0 auto}
.gl-faq details[open] summary::after{content:'\\2212'}
.gl-faq details p{margin-top:14px;color:#555;line-height:1.75;font-size:16px}
.gl-faq details a{color:#F45407}
.gl-contact{padding:96px 0;background:linear-gradient(135deg,#0F172A 0%,#1e293b 100%);color:#fff;scroll-margin-top:72px}
.gl-contact-grid{display:grid;grid-template-columns:1fr 1fr;gap:56px;align-items:start}
.gl-contact h2{color:#fff}
.gl-contact .gl-sub{color:#cbd5e1;font-size:17px;line-height:1.7;margin-bottom:28px}
.gl-contact .gl-check li{color:rgba(255,255,255,.9)}
.gl-contact .gl-check li::before{background-color:rgba(244,84,7,.18)}
.gl-contact-meta{margin-top:28px;padding-top:24px;border-top:1px solid rgba(255,255,255,.1);font-size:14px;color:#94a3b8;line-height:1.7}
.gl-contact-meta a{color:#fff}
.gl-formcard{background:#fff;border-radius:20px;padding:36px;box-shadow:0 25px 50px -12px rgba(0,0,0,.4);color:#101828}
.gl-formcard h3{font-size:22px;font-weight:600;color:#101828;margin-bottom:8px;text-align:center}
.gl-formcard .gl-formsub{font-size:14px;color:#667085;margin-bottom:24px;text-align:center}
.gl-formwrap{overflow:hidden;height:800px;border-radius:12px}
.gl-formwrap iframe{background:transparent;border:none;margin-top:-120px;width:100%;height:950px}
.gl-formalt{margin-top:20px;padding-top:20px;border-top:1px solid #e5e7eb;text-align:center;font-size:14px;color:#667085}
.gl-formalt a{color:#F45407;font-weight:500;text-decoration:none}
.gl-related{display:grid;grid-template-columns:repeat(3,1fr);gap:16px}
.gl-related a{display:block;padding:18px 20px;border:1px solid #eef0f3;border-radius:12px;text-decoration:none;color:#0F172A;font-weight:500;font-size:15px;line-height:1.45;background:#fff;transition:border-color .2s ease,color .2s ease}
.gl-related a:hover{border-color:#F45407;color:#F45407}
.gl-related small{display:block;color:#98a2b3;font-weight:400;font-size:13px;margin-top:4px}
@media (max-width:1024px){
  .gl-hero-grid,.gl-split,.gl-contact-grid{grid-template-columns:1fr;gap:40px}
  .gl-grid3,.gl-related{grid-template-columns:repeat(2,1fr)}
  .gl-steps,.gl-proof{grid-template-columns:repeat(2,1fr)}
}
@media (max-width:640px){
  .gl-hero{padding:104px 0 56px}
  .gl-lead{font-size:17px}
  .gl-stats{grid-template-columns:repeat(2,1fr);gap:20px}
  .gl-section,.gl-contact{padding:64px 0}
  .gl-grid3,.gl-steps,.gl-proof,.gl-related{grid-template-columns:1fr}
  .gl-card,.gl-tile{padding:22px}
  .gl-formcard{padding:22px 16px}
  .gl-ctas .gl-btn{flex:1 1 100%;text-align:center}
  .gl-band{padding:24px}
}
@media (prefers-reduced-motion:reduce){.gl-tile,.gl-btn{transition:none}.gl-tile:hover,.gl-btn-primary:hover{transform:none}}
</style>
""".replace('CHECK', CHECK_SVG)
