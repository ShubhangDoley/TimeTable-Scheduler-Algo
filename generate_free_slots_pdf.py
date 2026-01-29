import json
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch

def generate_daily_free_slots_pdf(json_path='free_slots.json', output_path='free_slots.pdf'):
    # Load Data
    try:
        with open(json_path, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: {json_path} not found. Please run generate_free_slots.py first.")
        return

    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
    except FileNotFoundError:
        print("Error: config.json not found.")
        return

    try:
        with open('rooms.json', 'r') as f:
            rooms_config = json.load(f)
    except FileNotFoundError:
        rooms_config = {}

    doc = SimpleDocTemplate(output_path, pagesize=landscape(A4), topMargin=30, bottomMargin=30)
    elements = []
    styles = getSampleStyleSheet()
    title_style = styles['Heading1']
    title_style.alignment = 1 # Center
    
    days = config['days']
    start_hour = config.get('start_hour', 9)
    end_hour = config.get('end_hour', 17)
    lab_subjects = config.get('labs', [])
    
    # Create slot labels for columns: "9:00", "10:00"...
    slots = [f"{h}:00" for h in range(start_hour, end_hour)]
    
    # Define Column Widths
    # Layout: First col is Room Name, others are time slots
    page_width = landscape(A4)[0] - 60 # margins
    col_width = (page_width - 1.2*inch) / len(slots)
    col_widths = [1.2*inch] + [col_width] * len(slots)

    # Sort rooms for consistent order
    room_names = sorted(data.keys())

    # Pre-calculate room types
    room_types = {}
    for room in room_names:
        subjs = rooms_config.get(room, [])
        is_lab = False
        for s in subjs:
            if s in lab_subjects:
                is_lab = True
                break
        room_types[room] = "LAB" if is_lab else "CLASS"

    # MAIN LOOP: Iterate by DAY
    for day_idx, day in enumerate(days):
        if day_idx > 0:
            elements.append(PageBreak())
            
        elements.append(Paragraph(f"Free Slots for {day}", title_style))
        elements.append(Spacer(1, 15))
        
        # Prepare Table Data for this Day
        # Header
        headers = ['Room'] + slots
        table_data = [headers]
        
        # Rows: One per Room
        for room in room_names:
            rtype = room_types.get(room, "")
            row_label = f"{room} ({rtype})"
            row_data = [row_label]
            
            # Check availability for this room on this day
            room_schedule = data.get(room, {})
            day_free_list = room_schedule.get(day, [])
            
            # Normalize free times
            free_start_times = []
            for slot_str in day_free_list:
                # "9:00 - 10:00" -> "9:00"
                parts = slot_str.split(' ')
                if parts:
                    free_start_times.append(parts[0])
            
            for slot_time in slots:
                if slot_time in free_start_times:
                    row_data.append("FREE")
                else:
                    row_data.append("") # Busy
            
            table_data.append(row_data)
        
        # Create Table
        t = Table(table_data, colWidths=col_widths)
        
        # Styles
        style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkgrey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            # First Column Styling (Room Names)
            ('BACKGROUND', (0, 1), (0, -1), colors.lightgrey),
            ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
        ])
        
        # Apply conditional coloring for FREE cells
        for r_idx, row in enumerate(table_data[1:], start=1):
            for c_idx, cell_content in enumerate(row[1:], start=1):
                if cell_content == "FREE":
                    style.add('BACKGROUND', (c_idx, r_idx), (c_idx, r_idx), colors.lightgreen)
                    style.add('TEXTCOLOR', (c_idx, r_idx), (c_idx, r_idx), colors.darkgreen)
                    style.add('FONTNAME', (c_idx, r_idx), (c_idx, r_idx), 'Helvetica-Bold')
                else:
                    # Busy slot
                    style.add('BACKGROUND', (c_idx, r_idx), (c_idx, r_idx), colors.whitesmoke)
        
        t.setStyle(style)
        elements.append(t)
    
    doc.build(elements)
    print(f"PDF generated successfully: {output_path}")

if __name__ == "__main__":
    generate_daily_free_slots_pdf()
