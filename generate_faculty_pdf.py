import json
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch

def generate_faculty_pdf(json_path='faculty_timetable.json', output_path='faculty_timetable.pdf'):
    # Load Data
    try:
        with open(json_path, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: {json_path} not found.")
        return

    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
    except FileNotFoundError:
        print("Error: config.json not found.")
        return

    doc = SimpleDocTemplate(output_path, pagesize=landscape(A4), topMargin=30, bottomMargin=30)
    elements = []
    styles = getSampleStyleSheet()
    title_style = styles['Heading1']
    title_style.alignment = 1 # Center
    
    # Title
    elements.append(Paragraph("Faculty Timetable & Availability Report", title_style))
    elements.append(Spacer(1, 20))
    
    days = config['days']
    # Get slot headers from the first entry of the first teacher
    first_teacher = next(iter(data))
    first_day = days[0]
    # slots list of dicts: time, status, ...
    slots_info = data[first_teacher][first_day]
    # Extract just time strings for headers
    # format: "H:00 - H+1:00" -> just show start time for header to save space? 
    # Or show "9-10". Let's show "9:00"
    slot_headers = []
    for s in slots_info:
        # s['time'] is "9:00 - 10:00"
        time_part = s['time'].split('-')[0].strip()
        slot_headers.append(time_part)
        
    # Column configuration
    # Col 1: Day
    # Cols 2+: Slots
    page_width = landscape(A4)[0] - 60
    col_width = (page_width - 0.8*inch) / len(slot_headers)
    col_widths = [0.8*inch] + [col_width] * len(slot_headers)

    teachers = sorted(data.keys())
    
    for t_idx, teacher in enumerate(teachers):
        if t_idx > 0:
            elements.append(PageBreak())
        
        elements.append(Paragraph(f"Faculty: {teacher}", styles['Heading2']))
        elements.append(Spacer(1, 10))
        
        t_data = data[teacher]
        
        # Table Header
        headers = ['Day'] + slot_headers
        table_rows = [headers]
        
        for day in days:
            row = [day]
            day_slots = t_data.get(day, [])
            
            for slot in day_slots:
                if slot['status'] == 'FREE':
                    row.append("FREE")
                else:
                    # Busy
                    # Show: Subject\nRoom\n(Batch)
                    subj = slot.get('subject', '')
                    room = slot.get('room', '')
                    batch = slot.get('batches', '')
                    
                    # Abbreviate?
                    # If batch list is long, truncate?
                    if len(batch) > 15:
                        # try to shorten "A1, A2, A3, A4" -> "All" or "A1..A4"?
                        pass
                        
                    content = f"{subj}\n{room}\n{batch}"
                    row.append(content)
            
            table_rows.append(row)
            
        # Create Table
        t = Table(table_rows, colWidths=col_widths)
        
        # Style
        style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkgrey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            # Content Cells
            ('FONTSIZE', (0, 1), (-1, -1), 8),
        ])
        
        # Coloring
        for r_idx, row in enumerate(table_rows[1:], start=1):
            for c_idx, content in enumerate(row[1:], start=1):
                if content == "FREE":
                    style.add('BACKGROUND', (c_idx, r_idx), (c_idx, r_idx), colors.lightgreen)
                    style.add('TEXTCOLOR', (c_idx, r_idx), (c_idx, r_idx), colors.darkgreen)
                    style.add('FONTNAME', (c_idx, r_idx), (c_idx, r_idx), 'Helvetica-Bold')
                else:
                    style.add('BACKGROUND', (c_idx, r_idx), (c_idx, r_idx), colors.lightblue)

        # Horizontal Merging for Consecutive Identical Cells (Labs)
        # Iterate over each row
        for r_idx in range(1, len(table_rows)):
            row = table_rows[r_idx]
            # Cols 1 to N
            start_col = 1
            while start_col < len(row):
                content = row[start_col]
                
                # Check consecutive columns
                end_col = start_col
                while end_col + 1 < len(row):
                    next_content = row[end_col + 1]
                    if next_content == content and content != "FREE":
                        end_col += 1
                    else:
                        break
                
                if end_col > start_col:
                    # Apply Span
                    # ReportLab span coords are (col, row)
                    style.add('SPAN', (start_col, r_idx), (end_col, r_idx))
                    
                start_col = end_col + 1

        t.setStyle(style)
        elements.append(t)
        
        # Add summary of workload?
        # Calculate load
        total_lectures = 0
        for d in days:
             for s in t_data.get(d, []):
                 if s['status'] == 'BUSY':
                     total_lectures += 1
        
        elements.append(Spacer(1, 10))
        elements.append(Paragraph(f"Total Workload: {total_lectures} hours/week", styles['Normal']))

    doc.build(elements)
    print(f"PDF generated successfully: {output_path}")

if __name__ == "__main__":
    generate_faculty_pdf()
