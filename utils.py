"""Automated PDF receipt generation with 80G certification using ReportLab."""
import io
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

def generate_pdf_receipt(donation):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    elements = []
    styles = getSampleStyleSheet()

    header_style = ParagraphStyle(
        'HeaderStyle',
        parent=styles['Heading1'],
        fontSize=22,
        textColor=colors.HexColor('#0d9488'),
        alignment=1,
        spaceAfter=4
    )
    sub_style = ParagraphStyle(
        'SubStyle',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#475569'),
        alignment=1,
        spaceAfter=15
    )
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#1e293b'),
        alignment=1,
        spaceAfter=15
    )

    elements.append(Paragraph("AASHRAY SEVA FOUNDATION", header_style))
    elements.append(Paragraph("Regd. Office: Nerul, Navi Mumbai - 400706 | IT 80G Exemption No: AAATA0000A/2026/80G", sub_style))
    elements.append(Paragraph(f"OFFICIAL DONATION RECEIPT & ACKNOWLEDGMENT", title_style))
    elements.append(Spacer(1, 10))

    receipt_data = [
        ["Receipt Number:", donation.receipt_id, "Date & Time:", donation.created_at.strftime('%d-%b-%Y %H:%M')],
        ["Donor Name:", donation.donor_name, "PAN / Tax ID:", donation.pan_number if donation.pan_number else 'N/A'],
        ["Donation Cause:", donation.category, "Payment Mode:", donation.payment_method],
        ["Transaction Ref:", donation.transaction_ref, "Direct Impact:", f"{donation.meals_funded} Meals Provided"],
        ["Total Contributed:", f"INR {donation.amount:,.2f}", "Tax Benefit:", "Eligible for 50% Deduction u/s 80G"]
    ]

    t = Table(receipt_data, colWidths=[130, 140, 120, 150])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8fafc')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#1e293b')),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
    ]))
    elements.append(t)
    elements.append(Spacer(1, 20))

    note_style = ParagraphStyle('NoteStyle', parent=styles['Normal'], fontSize=9, textColor=colors.HexColor('#64748b'))
    note_text = (
        "<b>Important Note:</b> This is an authentic computer-generated receipt for charity contribution towards "
        "Aashray Seva Foundation. Donations are exempt under Section 80G of the Income Tax Act, 1961. "
        "No goods or commercial services were provided in exchange for this contribution."
    )
    elements.append(Paragraph(note_text, note_style))

    doc.build(elements)
    buffer.seek(0)
    return buffer