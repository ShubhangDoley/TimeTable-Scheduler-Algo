import json
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch

def generate_free_slots_pdf(json_path='free_slots.json', output_path='free_slots.pdf'):
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

    doc = SimpleDocTemplate(output_path, pagesize=landscape(A4), topMargin=30, bottomMargin=30)
    elements = []
    styles = getSampleStyleSheet()
    title_style = styles['Heading1']
    title_style.alignment = 1 # Center
    
    # Title
    elements.append(Paragraph("Classroom Free Slots Report", title_style))
    elements.append(Spacer(1, 20))
    
    days = config['days']
    start_hour = config.get('start_hour', 9)
    end_hour = config.get('end_hour', 17)
    
    # Create slot labels for columns: "9:00", "10:00"...
    # Each column represents one hour block starting at that time.
    slots = [f"{h}:00" for h in range(start_hour, end_hour)]
    
    # Define Column Widths
    # Layout: First col is Day Name, others are time slots
    page_width = landscape(A4)[0] - 60 # margins
    col_width = (page_width - 0.8*inch) / len(slots)
    col_widths = [0.8*inch] + [col_width] * len(slots)

    # Load Rooms to determine type
    try:
        with open('rooms.json', 'r') as f:
            rooms_config = json.load(f)
    except FileNotFoundError:
        rooms_config = {}

    lab_subjects = config.get('labs', [])

    # Sort rooms for consistent order
    room_names = sorted(data.keys())
    
    for room_idx, room in enumerate(room_names):
        if room_idx > 0:
            if room_idx % 2 == 0:
                elements.append(PageBreak())
            else:
                elements.append(Spacer(1, 30))
        
        # Determine Room Type
        room_subjects = rooms_config.get(room, [])
        room_type = "CLASSROOM" # Default
        
        # If any subject hosted here is a lab, we consider it a Lab (or if majority)
        # Usually labs are dedicated.
        is_lab = False
        for subj in room_subjects:
            if subj in lab_subjects:
                is_lab = True
                break
        
        if is_lab:
            room_type = "LAB"
            
        elements.append(Paragraph(f"Room: {room} ({room_type})", styles['Heading2']))
        elements.append(Spacer(1, 10))
        
        # Prepare Table Data
        headers = ['Day'] + slots
        table_data = [headers]
        
        # Get free slots for this room
        room_free_schedule = data.get(room, {})
        
        for day in days:
            row_data = [day]
            day_free_list = room_free_schedule.get(day, [])
            
            # day_free_list contains strings like "9:00 - 10:00"
            # We need to normalize them to check against our slots
            # Extract start time from strings in list
            free_start_times = []
            for slot_str in day_free_list:
                # Expected format "H:00 - H+1:00"
                # Split by space and take first part "H:00"
                parts = slot_str.split(' ')
                if parts:
                    free_start_times.append(parts[0])
            
            for slot_time in slots:
                if slot_time in free_start_times:
                    row_data.append("FREE")
                else:
                    row_data.append("") # Busy/Occupied
            
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
                    style.add('TEXTCOLOR', (c_idx, r_idx), (c_idx, r_idx), colors.lightgrey)

        t.setStyle(style)
        elements.append(t)
    
    doc.build(elements)
    print(f"PDF generated successfully: {output_path}")

if __name__ == "__main__":
    generate_free_slots_pdf()
