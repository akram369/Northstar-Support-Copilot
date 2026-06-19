"""Generate the PDF knowledge-base policy used by the sample project."""

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "data" / "12_billing_security_policy.pdf"


def footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.HexColor("#667085"))
    canvas.drawString(0.7 * inch, 0.45 * inch, "Northstar Customer Policy Handbook | Internal support reference")
    canvas.drawRightString(7.8 * inch, 0.45 * inch, f"Page {doc.page}")
    canvas.restoreState()


def build():
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="Cover", parent=styles["Title"], alignment=TA_CENTER, textColor=colors.HexColor("#123B5D"), fontSize=28, leading=34, spaceAfter=18))
    styles.add(ParagraphStyle(name="Section", parent=styles["Heading1"], textColor=colors.HexColor("#123B5D"), fontSize=18, leading=22, spaceBefore=10, spaceAfter=10))
    styles.add(ParagraphStyle(name="Subsection", parent=styles["Heading2"], textColor=colors.HexColor("#246B83"), fontSize=12, leading=16, spaceBefore=8, spaceAfter=5))
    styles["BodyText"].fontSize = 10
    styles["BodyText"].leading = 15
    doc = SimpleDocTemplate(str(OUTPUT), pagesize=letter, rightMargin=0.7*inch, leftMargin=0.7*inch, topMargin=0.65*inch, bottomMargin=0.7*inch, title="Northstar Billing and Security Policy")
    story = [Spacer(1, 1.5*inch), Paragraph("Northstar Billing & Security Policy", styles["Cover"]), Paragraph("Customer support reference | Version 1.0", styles["Heading2"]), Spacer(1, 0.3*inch), Paragraph("This handbook defines the verified actions support may take for billing, account ownership, privacy, and security-sensitive requests.", styles["BodyText"]), PageBreak()]
    sections = [
        ("1. Billing and refunds", [
            ("Invoice access", "Organization Owners can download invoices from Settings > Billing > Invoices. Invoices are issued in the billing account currency and cannot be edited after issue. Legal name or address corrections apply to future invoices unless local law requires otherwise."),
            ("Refund review", "Support agents cannot promise or issue refunds in chat. Duplicate charges, incorrect plan renewals, and service-credit requests must be escalated to Billing with the organization ID, invoice number, charge date, and non-sensitive payment reference. Never collect full card numbers or bank credentials."),
            ("Plan cancellation", "An Owner can cancel renewal from Settings > Billing. Access continues through the paid term, after which the organization moves to read-only status for 30 days. Cancellation does not automatically create a refund."),
        ]),
        ("2. Account ownership", [
            ("Ownership transfer", "Only the current Owner can transfer ownership through Settings > Members. If the Owner is unavailable, support must escalate the case for organizational authorization and identity review. Support cannot bypass this process."),
            ("Identity verification", "Agents must use the approved verification workflow. Passwords, one-time codes, recovery codes, private keys, and full payment credentials must never be requested or accepted."),
        ]),
        ("3. Security and privacy", [
            ("Suspected compromise", "Immediately advise the customer to rotate exposed API tokens, reset affected credentials, and preserve relevant timestamps and request IDs. Escalate suspected account compromise or data exposure to the Security team. Do not speculate about breach scope."),
            ("Privacy requests", "Requests to access, correct, or delete personal data must be submitted through the privacy request process and escalated for verification. Support chat is not an approved identity-verification channel for privacy rights requests."),
            ("Safe evidence", "Collect organization ID, affected user, approximate time, request IDs, and a description of impact. Redact tokens, secrets, personal record contents, and payment data from screenshots and logs."),
        ]),
        ("4. Escalation service levels", [
            ("Routing", "Security incidents route to Security Operations; invoice and refund issues route to Billing; ownership and privacy issues route to Account Integrity. The receiving team confirms intake through the support case."),
            ("Time guidance", "Agents may share only published support-plan response targets. A response target is not a resolution promise. Never invent an estimated restoration, refund, or investigation completion time."),
        ]),
    ]
    for title, entries in sections:
        story.append(Paragraph(title, styles["Section"]))
        for heading, body in entries:
            story.append(Paragraph(heading, styles["Subsection"]))
            story.append(Paragraph(body, styles["BodyText"]))
            story.append(Spacer(1, 5))
    table = Table([["Issue", "Route"], ["Duplicate charge or refund", "Billing"], ["Account ownership dispute", "Account Integrity"], ["Suspected compromise", "Security Operations"], ["Personal data request", "Privacy"]], colWidths=[3.1*inch, 2.7*inch])
    table.setStyle(TableStyle([("BACKGROUND", (0,0), (-1,0), colors.HexColor("#123B5D")), ("TEXTCOLOR", (0,0), (-1,0), colors.white), ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"), ("GRID", (0,0), (-1,-1), 0.5, colors.HexColor("#AAB7C4")), ("VALIGN", (0,0), (-1,-1), "TOP"), ("PADDING", (0,0), (-1,-1), 7)]))
    story.extend([Spacer(1, 12), Paragraph("Escalation routing summary", styles["Section"]), table])
    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    print(OUTPUT)


if __name__ == "__main__":
    build()

