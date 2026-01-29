import json

def analyze_utilization():
    with open('timetable_full.json', 'r') as f:
        timetable = json.load(f)
    with open('rooms.json', 'r') as f:
        rooms_config = json.load(f)
    with open('config.json', 'r') as f:
        config = json.load(f)

    # 1. Calculate Supply (Total Slot Capacity)
    # 16 Rooms * 5 Days * 8 Slots = 640 Total Room-Slots available
    days = len(config['days'])
    hours = config['end_hour'] - config['start_hour']
    total_rooms = len(rooms_config)
    total_capacity_slots = total_rooms * days * hours

    # 2. Calculate Demand (Total Classes Scheduled)
    total_scheduled_slots = 0
    
    # We need to be careful not to double count.
    # The timetable is by Division -> Batch.
    # LECTURES are common to the whole division (usually).
    # LABS are specific to a batch.
    
    # Let's iterate and count actual unique room bookings.
    # A cleaner way is to look at our occupied matrix if we had it, 
    # but we can infer it from the timetable structure.
    
    # Actually, we can just iterate through every entry and if it has a room, it uses 1 slot of that room.
    # Since the timetable is hierarchical (Div -> Batch), 
    # - If type is LECTURE, it appears for all batches in that division. 
    #   BUT in the real world, 1 Lecture = 1 Room used.
    #   In the JSON, does "Lecture" appear duplicated for A1, A2, A3, A4?
    #   Let's check A1 vs A2 for a lecture.
    
    # Let's look at the implementation of our solver or the JSON structure.
    # If I look at DivA -> A1 -> Mon -> Slot1 (Stats, Room 6405)
    # And DivA -> A2 -> Mon -> Slot1 (Stats, Room 6405)
    # It is the SAME class. It consumes 1 Room-Slot, not 4.
    
    # So we should track unique (Day, Time, Room) tuples.
    
    consumed_slots = set()
    
    for div, batches in timetable.items():
        for batch, day_sched in batches.items():
            for day, slots in day_sched.items():
                for i, slot in enumerate(slots):
                    if isinstance(slot, dict) and 'room' in slot:
                        # Uniqueness key: Day + SlotIndex + Room
                        # If multiple batches share this, it's just 1 room usage.
                        key = (day, i, slot['room'])
                        consumed_slots.add(key)

    total_used = len(consumed_slots)
    
    print(f"--- Analysis ---")
    print(f"Total Rooms: {total_rooms}")
    print(f"Total Slots Available: {total_capacity_slots} (assuming {hours} hours/day * {days} days)")
    print(f"Total Slots Used: {total_used}")
    
    utilization = (total_used / total_capacity_slots) * 100
    print(f"Overall Utilization: {utilization:.2f}%")
    
    print("\n--- By Room Type ---")
    # Identify Lab vs Class rooms
    lab_subjects = config.get('labs', [])
    lab_rooms = set()
    class_rooms = set()
    
    for room, subjs in rooms_config.items():
        is_lab = any(s in lab_subjects for s in subjs)
        if is_lab:
            lab_rooms.add(room)
        else:
            class_rooms.add(room)
            
    print(f"Lab Rooms: {len(lab_rooms)}")
    print(f"Lecture Rooms: {len(class_rooms)}")
    
    # Calculate utilization per room
    room_usage = {r: 0 for r in rooms_config}
    for (d, i, r) in consumed_slots:
        if r in room_usage:
            room_usage[r] += 1
            
    print("\n--- Individual Room Utilization ---")
    for room in sorted(room_usage.keys()):
        u = room_usage[room]
        cap = days * hours
        pct = (u / cap) * 100
        rtype = "LAB" if room in lab_rooms else "CLASS"
        print(f"Room {room} ({rtype}): {pct:.1f}% ({u}/{cap} slots)")

if __name__ == "__main__":
    analyze_utilization()
