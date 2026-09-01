import io
from decimal import Decimal
from django.utils import timezone
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether
)
from reportlab.pdfgen import canvas
from apps.core.templatetags.currency_tags import clean_amount

class NumberedCanvas(canvas.Canvas):
    """
    Two-pass canvas to dynamically compute and print 'Page X of Y' and official header/footer.
    All header and footer text rendered in crisp pure black.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica-Bold", 8)
        self.setFillColor(colors.black)
        
        # Header Top Line & Header Text (All Black)
        self.setStrokeColor(colors.HexColor("#94a3b8"))
        self.setLineWidth(0.5)
        self.line(40, A4[1] - 40, A4[0] - 40, A4[1] - 40)
        self.drawString(40, A4[1] - 34, "TOUCH & SOLVE MICRO FINANCE CO-OPERATIVE • OFFICIAL SYSTEM RECORD")
        
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.black)
        self.drawRightString(A4[0] - 40, A4[1] - 34, timezone.now().strftime('%d %b %Y, %I:%M %p'))

        # Footer Bottom Line & Confidentiality Notice (All Black)
        self.line(40, 45, A4[0] - 40, 45)
        self.drawString(40, 32, "Confidential • Computer Generated Official Statement • Valid without physical seal")
        self.drawRightString(A4[0] - 40, 32, f"Page {self._pageNumber} of {page_count}")
        self.restoreState()


def get_pdf_styles():
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=15,
        leading=19,
        textColor=colors.black,
        alignment=0
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=12,
        textColor=colors.black
    )

    section_heading = ParagraphStyle(
        'SectionHeading',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10.5,
        leading=14,
        textColor=colors.black
    )

    cell_style = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=10,
        textColor=colors.black
    )

    cell_bold = ParagraphStyle(
        'TableCellBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=10,
        textColor=colors.black
    )

    cell_right = ParagraphStyle(
        'TableCellRight',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=10,
        textColor=colors.black,
        alignment=2
    )

    cell_right_bold = ParagraphStyle(
        'TableCellRightBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=10,
        textColor=colors.black,
        alignment=2
    )

    return {
        'title': title_style,
        'subtitle': subtitle_style,
        'heading': section_heading,
        'cell': cell_style,
        'cell_bold': cell_bold,
        'cell_right': cell_right,
        'cell_right_bold': cell_right_bold,
    }


def generate_savings_statement_pdf(member, account, transactions_list, start_date, end_date, opening_balance, total_deposits, total_withdrawals, closing_balance):
    """
    Generates a PDF for Savings & Withdrawal Statement with all black typography.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=40,
        rightMargin=40,
        topMargin=50,
        bottomMargin=55
    )
    
    st = get_pdf_styles()
    story = []

    # Title & Header
    story.append(Spacer(1, 10))
    story.append(Paragraph("TOUCH & SOLVE MICRO FINANCE CO-OPERATIVE", st['title']))
    story.append(Paragraph("Govt. Reg. Microfinance & Multi-Purpose Co-operative Society • Dhaka, Bangladesh", st['subtitle']))
    story.append(Spacer(1, 4))
    story.append(Paragraph(f"<b>OFFICIAL SAVINGS ACCOUNT STATEMENT</b> (Period: {start_date.strftime('%d %b %Y')} to {end_date.strftime('%d %b %Y')})", st['heading']))
    story.append(Spacer(1, 12))

    # Member Profile & Account Summary Box
    profile_data = [
        [
            Paragraph(f"<b>Member Name:</b> {member.user.get_full_name()}", st['cell']),
            Paragraph(f"<b>Account Number:</b> {account.account_number}", st['cell']),
            Paragraph(f"<b>Statement Date:</b> {timezone.now().strftime('%d %b %Y')}", st['cell'])
        ],
        [
            Paragraph(f"<b>Member ID:</b> {member.member_id}", st['cell']),
            Paragraph(f"<b>Phone:</b> {member.user.phone or 'N/A'}", st['cell']),
            Paragraph(f"<b>Officer:</b> {member.assigned_officer.get_full_name() if member.assigned_officer else 'Touch & Solve'}", st['cell'])
        ]
    ]
    t_profile = Table(profile_data, colWidths=[200, 160, 155])
    t_profile.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f8fafc')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#cbd5e1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(t_profile)
    story.append(Spacer(1, 12))

    # Financial Summary Highlights Table (Neutral background with Black Text)
    summary_data = [
        [
            Paragraph("<b>OPENING BALANCE</b>", st['cell_bold']),
            Paragraph("<b>TOTAL DEPOSITS (+)</b>", st['cell_bold']),
            Paragraph("<b>TOTAL WITHDRAWALS (-)</b>", st['cell_bold']),
            Paragraph("<b>CLOSING BALANCE</b>", st['cell_bold'])
        ],
        [
            Paragraph(f"{clean_amount(opening_balance)} BDT", st['cell_bold']),
            Paragraph(f"+{clean_amount(total_deposits)} BDT", st['cell_bold']),
            Paragraph(f"-{clean_amount(total_withdrawals)} BDT", st['cell_bold']),
            Paragraph(f"<b>{clean_amount(closing_balance)} BDT</b>", st['cell_bold'])
        ]
    ]
    t_summary = Table(summary_data, colWidths=[128, 129, 129, 129])
    t_summary.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#e2e8f0')),
        ('BACKGROUND', (0,1), (-1,1), colors.HexColor('#f8fafc')),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#94a3b8')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_summary)
    story.append(Spacer(1, 15))

    # Detailed Transaction Ledger Table
    story.append(Paragraph("<b>Detailed Transaction History</b>", st['heading']))
    story.append(Spacer(1, 6))

    ledger_data = [
        [
            Paragraph("<b>Date & Time</b>", st['cell_bold']),
            Paragraph("<b>Type</b>", st['cell_bold']),
            Paragraph("<b>Method / Reference</b>", st['cell_bold']),
            Paragraph("<b>Deposit (+)</b>", st['cell_right_bold']),
            Paragraph("<b>Withdraw (-)</b>", st['cell_right_bold']),
            Paragraph("<b>Balance</b>", st['cell_right_bold']),
            Paragraph("<b>Status</b>", st['cell_bold'])
        ]
    ]

    # Opening balance line
    ledger_data.append([
        Paragraph(start_date.strftime('%d %b %Y'), st['cell']),
        Paragraph("<b>B/F Opening</b>", st['cell']),
        Paragraph("Opening Balance Forward", st['cell']),
        Paragraph("&mdash;", st['cell_right']),
        Paragraph("&mdash;", st['cell_right']),
        Paragraph(f"{clean_amount(opening_balance)} BDT", st['cell_right_bold']),
        Paragraph("INIT", st['cell'])
    ])

    for item in transactions_list:
        trx = item['trx']
        is_dep = trx.transaction_type == 'DEPOSIT'
        dep_str = f"+{clean_amount(trx.amount)}" if is_dep and trx.status == 'APPROVED' else "&mdash;"
        with_str = f"-{clean_amount(trx.amount)}" if not is_dep and trx.status == 'APPROVED' else "&mdash;"
        bal_str = f"{clean_amount(item['running_balance'])} BDT" if item['running_balance'] is not None else "&mdash;"
        
        type_str = "<b>Deposit</b>" if is_dep else "<b>Withdrawal</b>"
        method_ref = f"{trx.get_payment_method_display()}" + (f" ({trx.reference_note})" if trx.reference_note else "")
        
        ledger_data.append([
            Paragraph(trx.created_at.strftime('%d %b %Y %I:%M%p'), st['cell']),
            Paragraph(type_str, st['cell']),
            Paragraph(method_ref[:35], st['cell']),
            Paragraph(dep_str, st['cell_right']),
            Paragraph(with_str, st['cell_right']),
            Paragraph(bal_str, st['cell_right']),
            Paragraph(trx.get_status_display(), st['cell'])
        ])

    # Closing balance summary row
    ledger_data.append([
        Paragraph(f"<b>Closing ({end_date.strftime('%d %b')})</b>", st['cell_bold']),
        Paragraph("<b>Total Period</b>", st['cell_bold']),
        Paragraph("Period Cumulative", st['cell_bold']),
        Paragraph(f"<b>+{clean_amount(total_deposits)}</b>", st['cell_right_bold']),
        Paragraph(f"<b>-{clean_amount(total_withdrawals)}</b>", st['cell_right_bold']),
        Paragraph(f"<b>{clean_amount(closing_balance)} BDT</b>", st['cell_right_bold']),
        Paragraph("FINAL", st['cell_bold'])
    ])

    t_ledger = Table(ledger_data, colWidths=[90, 60, 135, 65, 65, 65, 35], repeatRows=1)
    t_ledger.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#e2e8f0')),
        ('ROWBACKGROUNDS', (0,1), (-1,-2), [colors.white, colors.HexColor('#f8fafc')]),
        ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor('#f1f5f9')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#94a3b8')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_ledger)
    story.append(Spacer(1, 30))

    # Official Signatures Block
    sig_data = [
        [
            Paragraph("____________________________<br/><b>Prepared By (System)</b>", st['cell']),
            Paragraph("____________________________<br/><b>Account Officer</b>", st['cell']),
            Paragraph("____________________________<br/><b>Branch Manager</b>", st['cell'])
        ]
    ]
    t_sig = Table(sig_data, colWidths=[170, 170, 175])
    t_sig.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(KeepTogether([t_sig]))

    doc.build(story, canvasmaker=NumberedCanvas)
    buffer.seek(0)
    return buffer.getvalue()


def generate_loan_statement_pdf(loan, installments):
    """
    Generates a PDF for Loan & Amortization Repayment Statement with all black typography.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=40,
        rightMargin=40,
        topMargin=50,
        bottomMargin=55
    )
    st = get_pdf_styles()
    story = []

    # Title & Header
    story.append(Spacer(1, 10))
    story.append(Paragraph("TOUCH & SOLVE MICRO FINANCE CO-OPERATIVE", st['title']))
    story.append(Paragraph("Govt. Reg. Microfinance & Multi-Purpose Co-operative Society • Dhaka, Bangladesh", st['subtitle']))
    story.append(Spacer(1, 4))
    story.append(Paragraph(f"<b>OFFICIAL LOAN AMORTIZATION &amp; REPAYMENT STATEMENT</b> (Loan: {loan.loan_id})", st['heading']))
    story.append(Spacer(1, 12))

    # Loan Overview Info Table
    loan_info = [
        [
            Paragraph(f"<b>Borrower:</b> {loan.member.user.get_full_name()} ({loan.member.member_id})", st['cell']),
            Paragraph(f"<b>Principal Amount:</b> {clean_amount(loan.principal_amount)} BDT", st['cell']),
            Paragraph(f"<b>Interest Rate:</b> {loan.interest_rate}%", st['cell'])
        ],
        [
            Paragraph(f"<b>Purpose:</b> {loan.purpose}", st['cell']),
            Paragraph(f"<b>Total Payable:</b> {clean_amount(loan.total_payable)} BDT", st['cell']),
            Paragraph(f"<b>Duration:</b> {loan.duration_months} Months", st['cell'])
        ],
        [
            Paragraph(f"<b>Status:</b> <b>{loan.get_status_display()}</b>", st['cell']),
            Paragraph(f"<b>Total Repaid:</b> <b>{clean_amount(loan.total_paid)} BDT</b>", st['cell']),
            Paragraph(f"<b>Remaining:</b> <b>{clean_amount(loan.remaining_balance)} BDT</b>", st['cell'])
        ]
    ]
    t_info = Table(loan_info, colWidths=[200, 160, 155])
    t_info.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f8fafc')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#cbd5e1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_info)
    story.append(Spacer(1, 15))

    # Installments Table
    story.append(Paragraph("<b>Amortization Phases & Repayment Schedule</b>", st['heading']))
    story.append(Spacer(1, 6))

    inst_data = [
        [
            Paragraph("<b>Phase #</b>", st['cell_bold']),
            Paragraph("<b>Due Date</b>", st['cell_bold']),
            Paragraph("<b>Principal</b>", st['cell_right_bold']),
            Paragraph("<b>Interest</b>", st['cell_right_bold']),
            Paragraph("<b>Total Due</b>", st['cell_right_bold']),
            Paragraph("<b>Paid Amount</b>", st['cell_right_bold']),
            Paragraph("<b>Paid Date</b>", st['cell_bold']),
            Paragraph("<b>Status</b>", st['cell_bold'])
        ]
    ]

    for inst in installments:
        paid_amt = f"{clean_amount(inst.paid_amount)} BDT" if inst.paid_amount > 0 else "&mdash;"
        p_date = inst.paid_date.strftime('%d %b %Y') if inst.paid_date else "&mdash;"
        status_str = f"<b>{inst.get_status_display()}</b>"

        inst_data.append([
            Paragraph(f"Phase #{inst.installment_number}", st['cell_bold']),
            Paragraph(inst.due_date.strftime('%d %b %Y'), st['cell']),
            Paragraph(clean_amount(inst.principal_amount), st['cell_right']),
            Paragraph(clean_amount(inst.interest_amount), st['cell_right']),
            Paragraph(f"<b>{clean_amount(inst.total_amount)}</b>", st['cell_right']),
            Paragraph(paid_amt, st['cell_right_bold']),
            Paragraph(p_date, st['cell']),
            Paragraph(status_str, st['cell'])
        ])

    # Totals Row
    inst_data.append([
        Paragraph("<b>Total</b>", st['cell_bold']),
        Paragraph(f"<b>{installments.count()} Phases</b>", st['cell_bold']),
        Paragraph(f"<b>{clean_amount(loan.principal_amount)}</b>", st['cell_right_bold']),
        Paragraph(f"<b>{clean_amount(loan.total_interest)}</b>", st['cell_right_bold']),
        Paragraph(f"<b>{clean_amount(loan.total_payable)} BDT</b>", st['cell_right_bold']),
        Paragraph(f"<b>{clean_amount(loan.total_paid)} BDT</b>", st['cell_right_bold']),
        Paragraph("Remaining:", st['cell_bold']),
        Paragraph(f"<b>{clean_amount(loan.remaining_balance)} BDT</b>", st['cell_bold'])
    ])

    t_inst = Table(inst_data, colWidths=[60, 75, 65, 60, 75, 75, 65, 40], repeatRows=1)
    t_inst.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#e2e8f0')),
        ('ROWBACKGROUNDS', (0,1), (-1,-2), [colors.white, colors.HexColor('#f8fafc')]),
        ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor('#f1f5f9')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#94a3b8')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_inst)
    story.append(Spacer(1, 30))

    # Official Signatures Block
    sig_data = [
        [
            Paragraph("____________________________<br/><b>Borrower Signature</b>", st['cell']),
            Paragraph("____________________________<br/><b>Loan Officer</b>", st['cell']),
            Paragraph("____________________________<br/><b>Authorized Branch Manager</b>", st['cell'])
        ]
    ]
    t_sig = Table(sig_data, colWidths=[170, 170, 175])
    t_sig.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(KeepTogether([t_sig]))

    doc.build(story, canvasmaker=NumberedCanvas)
    buffer.seek(0)
    return buffer.getvalue()


def generate_daily_sheet_pdf(selected_date, deposits, installments_paid, due_installments, grand_total, total_deposit, total_installment, cash_deposits, digital_deposits, members):
    """
    Generates a PDF for Officer Daily Collection Sheet with all black typography.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=40,
        rightMargin=40,
        topMargin=50,
        bottomMargin=55
    )
    st = get_pdf_styles()
    story = []

    # Title & Header
    story.append(Spacer(1, 10))
    story.append(Paragraph("TOUCH & SOLVE MICRO FINANCE CO-OPERATIVE", st['title']))
    story.append(Paragraph("Govt. Reg. Microfinance & Multi-Purpose Co-operative Society • Dhaka, Bangladesh", st['subtitle']))
    story.append(Spacer(1, 4))
    story.append(Paragraph(f"<b>DAILY FIELD COLLECTION &amp; AUDIT SHEET</b> ({selected_date.strftime('%d %B %Y')})", st['heading']))
    story.append(Spacer(1, 12))

    # Summary Metrics Table
    sum_data = [
        [
            Paragraph("<b>GRAND TOTAL COLLECTION</b>", st['cell_bold']),
            Paragraph("<b>SAVINGS DEPOSITS</b>", st['cell_bold']),
            Paragraph("<b>LOAN REPAYMENTS</b>", st['cell_bold']),
            Paragraph("<b>CASH VS DIGITAL</b>", st['cell_bold'])
        ],
        [
            Paragraph(f"<b>{clean_amount(grand_total)} BDT</b>", st['cell_bold']),
            Paragraph(f"{clean_amount(total_deposit)} BDT", st['cell_bold']),
            Paragraph(f"{clean_amount(total_installment)} BDT", st['cell_bold']),
            Paragraph(f"Cash: {clean_amount(cash_deposits)} | Dig: {clean_amount(digital_deposits)}", st['cell'])
        ]
    ]
    t_sum = Table(sum_data, colWidths=[128, 129, 129, 129])
    t_sum.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#e2e8f0')),
        ('BACKGROUND', (0,1), (-1,1), colors.HexColor('#f8fafc')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#94a3b8')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_sum)
    story.append(Spacer(1, 15))

    # Realized Collections Table
    story.append(Paragraph("<b>1. Realized Field & Online Collections Today</b>", st['heading']))
    story.append(Spacer(1, 5))

    rec_data = [
        [
            Paragraph("<b>Time / Date</b>", st['cell_bold']),
            Paragraph("<b>Type</b>", st['cell_bold']),
            Paragraph("<b>Member</b>", st['cell_bold']),
            Paragraph("<b>Method / Channel</b>", st['cell_bold']),
            Paragraph("<b>Collector</b>", st['cell_bold']),
            Paragraph("<b>Amount</b>", st['cell_right_bold'])
        ]
    ]

    for dep in deposits:
        rec_data.append([
            Paragraph(dep.created_at.strftime('%I:%M %p'), st['cell']),
            Paragraph("<b>Savings Deposit</b>", st['cell']),
            Paragraph(f"{dep.account.member.member_id} ({dep.account.member.user.get_full_name()})", st['cell']),
            Paragraph(dep.get_payment_method_display(), st['cell']),
            Paragraph(dep.created_by.get_full_name() or dep.created_by.username, st['cell']),
            Paragraph(f"+{clean_amount(dep.amount)} BDT", st['cell_right_bold'])
        ])

    for inst in installments_paid:
        rec_data.append([
            Paragraph(inst.paid_date.strftime('%d %b') if inst.paid_date else '-', st['cell']),
            Paragraph(f"<b>Loan Phase #{inst.installment_number}</b>", st['cell']),
            Paragraph(f"{inst.loan.member.member_id} ({inst.loan.member.user.get_full_name()})", st['cell']),
            Paragraph(inst.get_payment_method_display(), st['cell']),
            Paragraph(inst.collected_by.get_full_name() if inst.collected_by else 'Officer', st['cell']),
            Paragraph(f"+{clean_amount(inst.paid_amount)} BDT", st['cell_right_bold'])
        ])

    if not deposits and not installments_paid:
        rec_data.append([
            Paragraph("No transactions recorded for this date.", st['cell']),
            Paragraph("", st['cell']),
            Paragraph("", st['cell']),
            Paragraph("", st['cell']),
            Paragraph("", st['cell']),
            Paragraph("-", st['cell_right'])
        ])
    else:
        rec_data.append([
            Paragraph("<b>Total Realized</b>", st['cell_bold']),
            Paragraph("", st['cell_bold']),
            Paragraph("", st['cell_bold']),
            Paragraph("", st['cell_bold']),
            Paragraph("", st['cell_bold']),
            Paragraph(f"<b>{clean_amount(grand_total)} BDT</b>", st['cell_right_bold'])
        ])

    t_rec = Table(rec_data, colWidths=[75, 80, 165, 85, 50, 60], repeatRows=1)
    t_rec.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#e2e8f0')),
        ('ROWBACKGROUNDS', (0,1), (-1,-2), [colors.white, colors.HexColor('#f8fafc')]),
        ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor('#f1f5f9')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#94a3b8')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_rec)
    story.append(Spacer(1, 20))

    # Field Roster Section
    story.append(Paragraph("<b>2. Member Field Roster & Balance Ledger</b>", st['heading']))
    story.append(Spacer(1, 5))

    roster_data = [
        [
            Paragraph("<b>Member ID &amp; Name</b>", st['cell_bold']),
            Paragraph("<b>Savings Bal</b>", st['cell_right_bold']),
            Paragraph("<b>Active Loan Due</b>", st['cell_bold']),
            Paragraph("<b>Deposit Coll.</b>", st['cell_bold']),
            Paragraph("<b>Loan Coll.</b>", st['cell_bold']),
            Paragraph("<b>Member Signature</b>", st['cell_bold'])
        ]
    ]

    for m in members:
        savings_bal = f"{clean_amount(m.savings_account.balance)} BDT" if hasattr(m, 'savings_account') else "0 BDT"
        loans_due = []
        for l in m.loans.all():
            if l.status == 'DISBURSED':
                loans_due.append(f"{l.loan_id}: {clean_amount(l.remaining_balance)}")
        loan_str = ", ".join(loans_due) if loans_due else "None"

        roster_data.append([
            Paragraph(f"<b>{m.member_id}</b><br/>{m.user.get_full_name()}", st['cell']),
            Paragraph(savings_bal, st['cell_right']),
            Paragraph(loan_str, st['cell']),
            Paragraph("[     ] BDT", st['cell']),
            Paragraph("[     ] BDT", st['cell']),
            Paragraph("________________", st['cell'])
        ])

    t_roster = Table(roster_data, colWidths=[135, 70, 110, 65, 65, 70], repeatRows=1)
    t_roster.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#e2e8f0')),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#f8fafc')]),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#94a3b8')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_roster)
    story.append(Spacer(1, 30))

    # Official Signatures Block
    sig_data = [
        [
            Paragraph("____________________________<br/><b>Field Collection Officer</b>", st['cell']),
            Paragraph("____________________________<br/><b>Audited &amp; Received By</b>", st['cell']),
            Paragraph("____________________________<br/><b>Branch Manager</b>", st['cell'])
        ]
    ]
    t_sig = Table(sig_data, colWidths=[170, 170, 175])
    t_sig.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(KeepTogether([t_sig]))

    doc.build(story, canvasmaker=NumberedCanvas)
    buffer.seek(0)
    return buffer.getvalue()
