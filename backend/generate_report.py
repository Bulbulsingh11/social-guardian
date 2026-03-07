# ============================================================
#  Social Guardian - Professional Legal Complaint PDF
# ============================================================

import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table,
    TableStyle, HRFlowable, KeepTogether
)

REPORTS_DIR = "reports"
os.makedirs(REPORTS_DIR, exist_ok=True)

# ── Colors ────────────────────────────────────────────────────
RED        = colors.HexColor('#B71C1C')
RED_LIGHT  = colors.HexColor('#FFEBEE')
RED_MID    = colors.HexColor('#EF5350')
NAVY       = colors.HexColor('#0D1B2A')
NAVY_LIGHT = colors.HexColor('#1A2E42')
GOLD       = colors.HexColor('#C9A84C')
GRAY_DARK  = colors.HexColor('#37474F')
GRAY_MID   = colors.HexColor('#78909C')
GRAY_LIGHT = colors.HexColor('#ECEFF1')
WHITE      = colors.white


def draw_page_border(canvas, doc):
    """Draw official-looking border and header on every page."""
    canvas.saveState()
    W, H = A4

    # Outer navy border
    canvas.setStrokeColor(NAVY)
    canvas.setLineWidth(3)
    canvas.rect(1*cm, 1*cm, W - 2*cm, H - 2*cm)

    # Inner gold border
    canvas.setStrokeColor(GOLD)
    canvas.setLineWidth(0.8)
    canvas.rect(1.2*cm, 1.2*cm, W - 2.4*cm, H - 2.4*cm)

    # Top header band
    canvas.setFillColor(NAVY)
    canvas.rect(1.2*cm, H - 2.8*cm, W - 2.4*cm, 1.55*cm, fill=1, stroke=0)

    # Gold line under header
    canvas.setFillColor(GOLD)
    canvas.rect(1.2*cm, H - 2.85*cm, W - 2.4*cm, 0.08*cm, fill=1, stroke=0)

    # Header text
    canvas.setFillColor(WHITE)
    canvas.setFont('Helvetica-Bold', 13)
    canvas.drawCentredString(W/2, H - 2.1*cm, "GOVERNMENT OF INDIA  —  CYBER CRIME COMPLAINT")

    canvas.setFont('Helvetica', 8)
    canvas.setFillColor(GOLD)
    canvas.drawCentredString(W/2, H - 2.55*cm, "Filed under IT Act 2000 & Indian Penal Code  |  National Cyber Crime Reporting Portal")

    # Bottom footer band
    canvas.setFillColor(NAVY)
    canvas.rect(1.2*cm, 1.2*cm, W - 2.4*cm, 0.72*cm, fill=1, stroke=0)

    canvas.setFillColor(GOLD)
    canvas.setFont('Helvetica', 7)
    canvas.drawString(1.6*cm, 1.48*cm, "SOCIAL GUARDIAN  —  AI-Powered Harassment Detection System")
    canvas.drawRightString(W - 1.6*cm, 1.48*cm, f"Page {doc.page}  |  cybercrime.gov.in")

    # Diagonal watermark
    canvas.saveState()
    canvas.translate(W/2, H/2)
    canvas.rotate(45)
    canvas.setFillColorRGB(0.85, 0.85, 0.85, alpha=0.18)
    canvas.setFont('Helvetica-Bold', 48)
    canvas.drawCentredString(0, 0, "EVIDENCE DOCUMENT")
    canvas.restoreState()

    canvas.restoreState()


def generate_report(victim_name, email, platform, post_url, flagged_comments):
    report_id = f"SG-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    filename  = f"{REPORTS_DIR}/{report_id}.pdf"
    date_str  = datetime.now().strftime("%d %B %Y")
    time_str  = datetime.now().strftime("%I:%M %p")

    doc = SimpleDocTemplate(
        filename,
        pagesize=A4,
        rightMargin=2.2*cm, leftMargin=2.2*cm,
        topMargin=3.6*cm,   bottomMargin=2.2*cm,
        title="Online Harassment Complaint",
        author="Social Guardian",
    )

    # ── Helper styles ──────────────────────────────────────
    def st(name, **kw):
        return ParagraphStyle(name, **kw)

    s_title   = st('T',  fontSize=17, fontName='Helvetica-Bold', textColor=NAVY,      alignment=TA_CENTER, spaceAfter=2, spaceBefore=4)
    s_sub     = st('S',  fontSize=9,  fontName='Helvetica',      textColor=GRAY_MID,  alignment=TA_CENTER, spaceAfter=12)
    s_sec     = st('SH', fontSize=9,  fontName='Helvetica-Bold', textColor=WHITE,     alignment=TA_LEFT,   spaceAfter=0, spaceBefore=0, leftIndent=8)
    s_norm    = st('N',  fontSize=9,  fontName='Helvetica',      textColor=GRAY_DARK, spaceAfter=3)
    s_comment = st('C',  fontSize=10, fontName='Helvetica-BoldOblique', textColor=RED, leftIndent=8, spaceAfter=0)
    s_legal   = st('L',  fontSize=9,  fontName='Helvetica',      textColor=GRAY_DARK, leading=15, alignment=TA_JUSTIFY, spaceAfter=5)
    s_footer  = st('F',  fontSize=8,  fontName='Helvetica',      textColor=GRAY_MID,  alignment=TA_CENTER)

    def banner(title):
        t = Table([[Paragraph(title, s_sec)]], colWidths=[16.6*cm])
        t.setStyle(TableStyle([
            ('BACKGROUND',    (0,0), (-1,-1), NAVY),
            ('TOPPADDING',    (0,0), (-1,-1), 6),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
            ('LEFTPADDING',   (0,0), (-1,-1), 10),
        ]))
        return t

    story = []

    # ── TITLE BLOCK ────────────────────────────────────────
    story.append(Spacer(1, 0.1*cm))
    story.append(Paragraph("ONLINE HARASSMENT COMPLAINT", s_title))
    story.append(Paragraph("AI-Generated Evidence Report  —  For Submission to Cyber Crime Portal", s_sub))
    story.append(HRFlowable(width="100%", thickness=1.5, color=GOLD))
    story.append(Spacer(1, 0.25*cm))

    # Meta row
    meta = Table([[
        Paragraph(f"<b>Report ID:</b>  {report_id}", s_norm),
        Paragraph(f"<b>Date:</b>  {date_str}", s_norm),
        Paragraph(f"<b>Time:</b>  {time_str}", s_norm),
        Paragraph("<b>Status:</b>  <font color='#B71C1C'>EVIDENCE COLLECTED</font>", s_norm),
    ]], colWidths=[5*cm, 3.6*cm, 3.5*cm, 4.5*cm])
    meta.setStyle(TableStyle([
        ('BACKGROUND',    (0,0), (-1,-1), GRAY_LIGHT),
        ('TOPPADDING',    (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING',   (0,0), (-1,-1), 8),
        ('LINEBELOW',     (0,0), (-1,-1), 1, GOLD),
    ]))
    story.append(meta)
    story.append(Spacer(1, 0.35*cm))

    # ── SECTION 1: COMPLAINANT ─────────────────────────────
    story.append(banner("SECTION 1  —  COMPLAINANT DETAILS"))
    story.append(Spacer(1, 0.1*cm))

    comp = Table([
        ["Full Name",   victim_name,  "Email Address", email],
        ["Platform",    platform,     "Post / Page URL", post_url],
    ], colWidths=[3*cm, 5.3*cm, 3.5*cm, 4.8*cm])
    comp.setStyle(TableStyle([
        ('FONTNAME',  (0,0), (0,-1), 'Helvetica-Bold'),
        ('FONTNAME',  (2,0), (2,-1), 'Helvetica-Bold'),
        ('FONTNAME',  (1,0), (1,-1), 'Helvetica'),
        ('FONTNAME',  (3,0), (3,-1), 'Helvetica'),
        ('FONTSIZE',  (0,0), (-1,-1), 9),
        ('TEXTCOLOR', (0,0), (0,-1), NAVY),
        ('TEXTCOLOR', (2,0), (2,-1), NAVY),
        ('TEXTCOLOR', (1,0), (1,-1), GRAY_DARK),
        ('TEXTCOLOR', (3,0), (3,-1), GRAY_DARK),
        ('ROWBACKGROUNDS', (0,0), (-1,-1), [GRAY_LIGHT, WHITE]),
        ('TOPPADDING',    (0,0), (-1,-1), 7),
        ('BOTTOMPADDING', (0,0), (-1,-1), 7),
        ('LEFTPADDING',   (0,0), (-1,-1), 10),
        ('GRID', (0,0), (-1,-1), 0.4, colors.HexColor('#CFD8DC')),
    ]))
    story.append(comp)
    story.append(Spacer(1, 0.35*cm))

    # ── SECTION 2: SUMMARY ────────────────────────────────
    story.append(banner("SECTION 2  —  INCIDENT SUMMARY"))
    story.append(Spacer(1, 0.1*cm))

    total   = len(flagged_comments)
    threats = sum(1 for c in flagged_comments if c.get('threat', 0) > 0.5)
    insults = sum(1 for c in flagged_comments if c.get('insult', 0) > 0.6)
    high    = sum(1 for c in flagged_comments if c.get('toxicity', 0) > 0.8)

    summ = Table([
        ["TOTAL ABUSIVE COMMENTS", str(total),   "HIGH SEVERITY COMMENTS", str(high)],
        ["THREATS DETECTED",       str(threats), "INSULTS DETECTED",       str(insults)],
    ], colWidths=[5.2*cm, 2.6*cm, 5.2*cm, 3.6*cm])
    summ.setStyle(TableStyle([
        ('FONTNAME',  (0,0), (0,-1), 'Helvetica-Bold'),
        ('FONTNAME',  (2,0), (2,-1), 'Helvetica-Bold'),
        ('FONTNAME',  (1,0), (1,-1), 'Helvetica-Bold'),
        ('FONTNAME',  (3,0), (3,-1), 'Helvetica-Bold'),
        ('FONTSIZE',  (0,0), (-1,-1), 9),
        ('TEXTCOLOR', (0,0), (0,-1), NAVY),
        ('TEXTCOLOR', (2,0), (2,-1), NAVY),
        ('TEXTCOLOR', (1,0), (1,-1), RED),
        ('TEXTCOLOR', (3,0), (3,-1), RED),
        ('ROWBACKGROUNDS', (0,0), (-1,-1), [RED_LIGHT, WHITE]),
        ('TOPPADDING',    (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('LEFTPADDING',   (0,0), (-1,-1), 10),
        ('GRID', (0,0), (-1,-1), 0.4, colors.HexColor('#FFCDD2')),
    ]))
    story.append(summ)
    story.append(Spacer(1, 0.35*cm))

    # ── SECTION 3: EVIDENCE ───────────────────────────────
    story.append(banner("SECTION 3  —  HARASSMENT EVIDENCE"))
    story.append(Spacer(1, 0.2*cm))

    def score_bar(val):
        filled = int(round(val * 10))
        return '█' * filled + '░' * (10 - filled)

    for i, item in enumerate(flagged_comments, 1):
        username = item.get('username', 'Unknown')
        comment  = item.get('comment', '')
        toxicity = item.get('toxicity', 0)
        threat   = item.get('threat',   0)
        insult   = item.get('insult',   0)
        sev      = "EXTREME" if toxicity > 0.85 else "HIGH" if toxicity > 0.7 else "MEDIUM"
        sev_col  = '#B71C1C' if sev == "EXTREME" else '#E53935' if sev == "HIGH" else '#FB8C00'

        # Header row
        hdr = Table([[
            Paragraph(f"<b>EVIDENCE  #{i}</b>", st('eh', fontSize=9, fontName='Helvetica-Bold', textColor=WHITE)),
            Paragraph(f"<b>Offender Handle:</b>  @{username}", st('eu', fontSize=9, fontName='Helvetica-Bold', textColor=GOLD)),
            Paragraph(f"Severity: <font color='{sev_col}'><b>{sev}</b></font>",
                      st('es', fontSize=9, fontName='Helvetica-Bold', textColor=WHITE, alignment=TA_RIGHT)),
        ]], colWidths=[3.5*cm, 8.5*cm, 4.6*cm])
        hdr.setStyle(TableStyle([
            ('BACKGROUND',    (0,0), (-1,-1), NAVY_LIGHT),
            ('TOPPADDING',    (0,0), (-1,-1), 6),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
            ('LEFTPADDING',   (0,0), (-1,-1), 10),
            ('RIGHTPADDING',  (2,0), (2,0),   10),
        ]))

        # Comment row
        cmt = Table([[Paragraph(f'"{comment}"', s_comment)]], colWidths=[16.6*cm])
        cmt.setStyle(TableStyle([
            ('BACKGROUND',    (0,0), (-1,-1), RED_LIGHT),
            ('TOPPADDING',    (0,0), (-1,-1), 8),
            ('BOTTOMPADDING', (0,0), (-1,-1), 8),
            ('LEFTPADDING',   (0,0), (-1,-1), 12),
            ('LINEBEFORE',    (0,0), (0,-1),  3, RED),
        ]))

        # Scores row
        scr = Table([[
            Paragraph("<b>Toxicity</b>", s_norm),
            Paragraph(f"{toxicity:.2f}  {score_bar(toxicity)}  {'HIGH' if toxicity>0.6 else 'LOW'}", s_norm),
            Paragraph("<b>Threat</b>", s_norm),
            Paragraph(f"{threat:.2f}  {score_bar(threat)}  {'HIGH' if threat>0.5 else 'LOW'}", s_norm),
            Paragraph("<b>Insult</b>", s_norm),
            Paragraph(f"{insult:.2f}  {score_bar(insult)}  {'HIGH' if insult>0.6 else 'LOW'}", s_norm),
        ]], colWidths=[1.8*cm, 4*cm, 1.6*cm, 3.9*cm, 1.5*cm, 3.8*cm])
        scr.setStyle(TableStyle([
            ('FONTSIZE',      (0,0), (-1,-1), 8.5),
            ('BACKGROUND',    (0,0), (-1,-1), GRAY_LIGHT),
            ('TOPPADDING',    (0,0), (-1,-1), 6),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
            ('LEFTPADDING',   (0,0), (-1,-1), 8),
            ('LINEABOVE',     (0,0), (-1,0),  0.4, colors.HexColor('#CFD8DC')),
        ]))

        # Status row
        sts = Table([[Paragraph(
            "  STATUS:  FLAGGED  —  ABUSIVE CONTENT DETECTED  —  ELIGIBLE FOR CYBER CRIME COMPLAINT",
            st('st', fontSize=8.5, fontName='Helvetica-Bold', textColor=WHITE, alignment=TA_CENTER)
        )]], colWidths=[16.6*cm])
        sts.setStyle(TableStyle([
            ('BACKGROUND',    (0,0), (-1,-1), RED),
            ('TOPPADDING',    (0,0), (-1,-1), 5),
            ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ]))

        story.append(KeepTogether([hdr, cmt, scr, sts]))
        story.append(Spacer(1, 0.3*cm))

    # ── SECTION 4: LAWS ───────────────────────────────────
    story.append(banner("SECTION 4  —  APPLICABLE LAWS & SECTIONS"))
    story.append(Spacer(1, 0.1*cm))

    laws = Table([
        ["IT Act 2000 — Sec 66A",  "Punishment for sending offensive / threatening messages electronically"],
        ["IT Act 2000 — Sec 67",   "Publishing obscene or defamatory material in electronic form"],
        ["IPC Section 354D",       "Cyberstalking — monitoring a woman's activity on the internet"],
        ["IPC Section 507",        "Criminal intimidation by anonymous communication"],
        ["IPC Section 499 / 500",  "Defamation and its punishment through electronic media"],
        ["IPC Section 503",        "Criminal intimidation — threat to cause harm to person or reputation"],
    ], colWidths=[5*cm, 11.6*cm])
    laws.setStyle(TableStyle([
        ('FONTNAME',  (0,0), (0,-1), 'Helvetica-Bold'),
        ('FONTNAME',  (1,0), (1,-1), 'Helvetica'),
        ('FONTSIZE',  (0,0), (-1,-1), 8.5),
        ('TEXTCOLOR', (0,0), (0,-1), NAVY),
        ('TEXTCOLOR', (1,0), (1,-1), GRAY_DARK),
        ('ROWBACKGROUNDS', (0,0), (-1,-1), [GRAY_LIGHT, WHITE]),
        ('TOPPADDING',    (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING',   (0,0), (-1,-1), 10),
        ('GRID', (0,0), (-1,-1), 0.4, colors.HexColor('#CFD8DC')),
    ]))
    story.append(laws)
    story.append(Spacer(1, 0.35*cm))

    # ── SECTION 5: DECLARATION ────────────────────────────
    story.append(banner("SECTION 5  —  DECLARATION & SIGNATURE"))
    story.append(Spacer(1, 0.2*cm))

    story.append(Paragraph(
        f"I, <b>{victim_name}</b>, solemnly declare that the information provided in this complaint "
        f"is true and correct to the best of my knowledge. The above-mentioned comments were directed "
        f"at me on <b>{platform}</b> and have caused me significant distress. I hereby request the "
        f"concerned authorities to take appropriate legal action against the offenders under the "
        f"applicable provisions of the IT Act 2000 and the Indian Penal Code.",
        s_legal
    ))
    story.append(Paragraph(
        f"This complaint has been prepared with AI-assisted evidence collection by <b>Social Guardian</b> "
        f"and is submitted for official registration at the "
        f"<b>National Cyber Crime Reporting Portal — cybercrime.gov.in</b>.",
        s_legal
    ))
    story.append(Spacer(1, 0.5*cm))

    sig = Table([[
        Paragraph("Complainant Signature\n\n\n___________________________\n" + victim_name, s_norm),
        Paragraph("Date\n\n\n___________________________\n" + date_str, s_norm),
        Paragraph("Place\n\n\n___________________________\n ", s_norm),
    ]], colWidths=[5.5*cm, 5.5*cm, 5.6*cm])
    sig.setStyle(TableStyle([
        ('FONTSIZE',      (0,0), (-1,-1), 9),
        ('TOPPADDING',    (0,0), (-1,-1), 10),
        ('BOTTOMPADDING', (0,0), (-1,-1), 10),
        ('LEFTPADDING',   (0,0), (-1,-1), 10),
        ('BOX', (0,0), (0,-1), 0.5, colors.HexColor('#CFD8DC')),
        ('BOX', (1,0), (1,-1), 0.5, colors.HexColor('#CFD8DC')),
        ('BOX', (2,0), (2,-1), 0.5, colors.HexColor('#CFD8DC')),
    ]))
    story.append(sig)
    story.append(Spacer(1, 0.3*cm))
    story.append(HRFlowable(width="100%", thickness=1.5, color=GOLD))
    story.append(Spacer(1, 0.1*cm))
    story.append(Paragraph(
        f"Report ID: {report_id}  |  Generated by Social Guardian v1.0  |  {date_str}  |  cybercrime.gov.in",
        s_footer
    ))

    doc.build(story, onFirstPage=draw_page_border, onLaterPages=draw_page_border)
    print(f"Report saved: {filename}")
    return filename