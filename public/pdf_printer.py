from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer,  Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from datetime import datetime
from models.orders import Order, OrderItem
from models.customers import Customer
from models.stores_info import StoreInfo
from reportlab.lib.enums import TA_RIGHT, TA_LEFT, TA_CENTER

def generate_order_pdf(order_id):
    """ Genera il PDF del Documento di Trasporto (DDT) con IVA scorporata """
    iva_percentage = 22  # IVA 22%

    order = Order.query.get(order_id)
    if not order:
        return None  # Se l'ordine non esiste

    customer = Customer.query.get(order.customer_id) if order.customer_id else None
    order_items = OrderItem.query.filter_by(order_id=order_id).all()
    store_info = StoreInfo.query.filter_by(shop_name=order.shop_name).first()

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)

    styles = getSampleStyleSheet()
    elements = []

    # 📌 **Titolo**
    elements.append(Paragraph("TRANSPORT DOCUMENT (DDT)", styles["Title"]))
    elements.append(Spacer(1, 12))

    # 📌 **Dati Mittente (StoreInfo)**
    sender_info = f"""
    <b>Sender:</b> {store_info.owner_name if store_info else "Store Name"}<br/>
    <b>Email:</b> {store_info.email if store_info else "N/A"}<br/>
    <b>Phone:</b> {store_info.phone if store_info and store_info.phone else "N/A"}
    """
    elements.append(Paragraph(sender_info, styles["Normal"]))
    elements.append(Spacer(1, 12))

    # 📌 **Dati Destinatario**
    receiver_info = f"""
    <b>Receiver:</b> {customer.first_name} {customer.last_name}<br/>
    <b>Address:</b> {customer.address or 'N/A'}, {customer.city or 'N/A'}<br/>
    <b>Email:</b> {customer.email}<br/>
    <b>Phone:</b> {customer.phone or 'N/A'}
    """
    elements.append(Paragraph(receiver_info, styles["Normal"]))
    elements.append(Spacer(1, 12))

    # 📌 **Dati Ordine**
    order_details = f"""
    <b>Order No:</b> {order.order_number}<br/>
    <b>Status:</b> {order.status}<br/>
    <b>Created:</b> {order.created_at.strftime('%d/%m/%Y')}<br/>
    <b>Last Update:</b> {order.updated_at.strftime('%d/%m/%Y')}
    """
    elements.append(Paragraph(order_details, styles["Normal"]))
    elements.append(Spacer(1, 12))

    # 📌 **Tabella Prodotti**
    data = [["Product", "Qty", "Unit Price (€)", "Subtotal (€)", "Subtotal ex. VAT (€)"]]
    total_price = 0
    total_net_price = 0

    for item in order_items:
        product_name = item.product.name if item.product else "Unknown Product"
        subtotal = item.subtotal  # Prezzo totale del prodotto con IVA inclusa
        subtotal_ex_vat = subtotal / (1 + iva_percentage / 100)  # Scorporo IVA
        total_price += subtotal
        total_net_price += subtotal_ex_vat

        data.append([product_name, str(item.quantity), f"{item.price:.2f}", f"{subtotal:.2f}", f"{subtotal_ex_vat:.2f}"])

    # 📌 **Calcolo IVA**
    iva_amount = total_price - total_net_price  # IVA scorporata
    total_with_iva = total_price  # Il totale rimane invariato perché già incluso

    # 📌 **Righe Finali**
    data.append(["", "", "", "Subtotal:", f"€{total_net_price:.2f}"])
    data.append(["", "", "", f"VAT {iva_percentage}%:", f"€{iva_amount:.2f}"])
    data.append(["", "", "", "Total (incl. VAT):", f"€{total_with_iva:.2f}"])

    # 📌 **Stile Tabella**
    table = Table(data, colWidths=[160, 50, 70, 80, 100])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.black),  # Header sfondo nero
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),  # Testo header bianco
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),  # Allineamento testo
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),  # Font header
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),  # Font corpo tabella
        ('GRID', (0, 0), (-1, -1), 1, colors.black),  # Bordo nero
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),  # Sfondo grigio
        ('TEXTCOLOR', (-1, -1), (-1, -1), colors.black),  # Totale in rosso
    ]))

    elements.append(table)
    elements.append(Spacer(1, 20))

    # 📌 **Spazio Firma**
    elements.append(Paragraph("Receiver Signature: __________________________", styles["Normal"]))
    elements.append(Paragraph("Date: ____/____/______", styles["Normal"]))

    # 📌 **Generazione PDF**
    doc.build(elements)
    buffer.seek(0)

    return buffer



def generate_invoice_pdf(order_id):
    """Genera una fattura PDF con design professionale"""
    iva_percentage = 22  # IVA al 22%

    order = Order.query.get(order_id)
    if not order:
        return None

    customer = Customer.query.get(order.customer_id) if order.customer_id else None
    order_items = OrderItem.query.filter_by(order_id=order_id).all()
    store_info = StoreInfo.query.filter_by(shop_name=order.shop_name).first()

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=20*mm, leftMargin=20*mm)
    
    styles = getSampleStyleSheet()
    elements = []
    
    # Stili personalizzati
    styles.add(ParagraphStyle(name='RightAlign', alignment=TA_RIGHT, parent=styles['Normal']))
    styles.add(ParagraphStyle(name='LeftAlign', alignment=TA_LEFT, parent=styles['Normal']))
    styles.add(ParagraphStyle(name='AccentColor', textColor=colors.HexColor('#2E5984'), parent=styles['Title']))

    # Intestazione con logo
    if store_info and store_info.logo_url:
        logo = Image(store_info.logo_url, width=100, height=40)
        elements.append(logo)
    
    # Titolo con design moderno
    title_table = Table([
        [Paragraph(f"<font size=14 color='#2E5984'><b>INVOICE</b></font>"), 
         Paragraph(f"<font size=10>Date: {datetime.now().strftime('%d %b %Y')}</font>", styles['RightAlign'])]
    ], colWidths=[doc.width*0.7, doc.width*0.3])
    elements.append(title_table)
    elements.append(Spacer(1, 15))

    # Sezione mittente/destinatario in due colonne
    sender_receiver = [
        [
            Paragraph(f"<b>From:</b><br/>"
                      f"{store_info.shop_name if store_info else ''}<br/>"
                      f"{store_info.address if store_info else ''}<br/>"
                      f"{store_info.city if store_info else ''}<br/>"
                      f"VAT: {store_info.vat_number if store_info else ''}", styles['LeftAlign']),
            
            Paragraph(f"<b>Bill To:</b><br/>"
                      f"{customer.first_name} {customer.last_name}<br/>"
                      f"{customer.address or ''}<br/>"
                      f"{customer.postal_code or ''} {customer.city or ''}<br/>"
                      f"{customer.country or ''}", styles['LeftAlign'])
        ]
    ]
    
    sr_table = Table(sender_receiver, colWidths=[doc.width*0.5, doc.width*0.5])
    sr_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 10),
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F0F8FF')),
    ]))
    elements.append(sr_table)
    elements.append(Spacer(1, 20))

    # Dettagli ordine
    order_details = [
        ["Invoice #:", order.order_number, "Due Date:", order.updated_at.strftime('%d %b %Y')],
        ["Order Date:", order.created_at.strftime('%d %b %Y'), "Payment Method:", order.payment_method],
        ["Order Status:", order.status, "Shipping Method:", order.shipping_method]
    ]
    
    details_table = Table(order_details, colWidths=[60, 120, 80, 120])
    details_table.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOX', (0,0), (-1,-1), 0.5, colors.lightgrey),
        ('BACKGROUND', (0,0), (-1,-1), colors.white),
    ]))
    elements.append(details_table)
    elements.append(Spacer(1, 15))

    # Tabella prodotti
    data = [["Description", "Qty", "Unit Price", "VAT", "Total"]]
    total_net = 0
    total_vat = 0
    total_with_vat = 0

    for item in order_items:
        product_name = item.product.name if item.product else "Unknown Product"
        subtotal_ex_vat = item.subtotal / (1 + iva_percentage / 100)
        vat_amount = item.subtotal - subtotal_ex_vat
        
        data.append([
            Paragraph(f"<b>{product_name}</b><br/><font size=8>SKU: {item.product.sku if item.product else 'N/A'}</font>", styles['LeftAlign']),
            str(item.quantity),
            f"€{item.price:.2f}",
            f"€{vat_amount:.2f}",
            f"€{item.subtotal:.2f}"
        ])
        total_net += subtotal_ex_vat
        total_vat += vat_amount
        total_with_vat += item.subtotal

    # Totali
    data.extend([
        ['']*5,
        ['', '', '', 'Subtotal:', f"€{total_net:.2f}"],
        ['', '', '', f"VAT ({iva_percentage}%):", f"€{total_vat:.2f}"],
        ['', '', '', Paragraph("<b>Total Due:</b>", styles['RightAlign']), Paragraph(f"<b>€{total_with_vat:.2f}</b>", styles['RightAlign'])]
    ])

    item_table = Table(data, colWidths=[doc.width*0.4, 40, 60, 60, 80])
    item_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#2E5984')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('ALIGN', (1,0), (-1,-1), 'RIGHT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('GRID', (0,0), (-1,-4), 0.5, colors.lightgrey),
        ('LINEABOVE', (-2,-3), (-1,-3), 0.5, colors.lightgrey),
        ('LINEABOVE', (-2,-1), (-1,-1), 1.5, colors.HexColor('#2E5984')),
        ('BOLD', (-2,-1), (-1,-1)),
    ]))
    elements.append(item_table)
    elements.append(Spacer(1, 25))

    # Note e firma
    footer = [
        [Paragraph("Payment Terms:<br/>Net 30 days. Late payments subject to 1.5% monthly interest.", styles['LeftAlign']),
         Paragraph("Authorized Signature<br/><br/><br/>_________________________", styles['RightAlign'])]
    ]
    
    footer_table = Table(footer, colWidths=[doc.width*0.6, doc.width*0.4])
    elements.append(footer_table)
    
    # Footer aziendale
    elements.append(Spacer(1, 20))
    elements.append(Paragraph(
        f"{store_info.shop_name if store_info else ''} | Registered in Italy | VAT {store_info.vat_number if store_info else ''} | {store_info.phone if store_info else ''} | {store_info.email}",
        ParagraphStyle(name='Footer', alignment=TA_CENTER, fontSize=8, textColor=colors.grey))
    )

    doc.build(elements)
    buffer.seek(0)
    return buffer