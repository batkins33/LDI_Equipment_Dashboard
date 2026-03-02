"""Generate realistic mock data for Equipment Hours Validation demo."""

import json
import random
from datetime import datetime, timedelta
from pathlib import Path


def generate_mock_heavyjob():
    """Generate mock HeavyJob timecard data."""
    jobs = [
        {"job_id": "HJ-001", "job_name": "Highway Expansion Phase 1", "business_unit": "BU-001"},
        {"job_id": "HJ-002", "job_name": "Bridge Repair", "business_unit": "BU-001"},
        {"job_id": "HJ-003", "job_name": "Parking Lot Paving", "business_unit": "BU-002"},
        {"job_id": "HJ-004", "job_name": "Site Prep & Grading", "business_unit": "BU-002"},
        {"job_id": "HJ-005", "job_name": "Utility Trenching", "business_unit": "BU-003"},
    ]
    
    equipment = [
        {"equipment_id": "EQ-001", "equipment_code": "CAT320", "type": "Excavator"},
        {"equipment_id": "EQ-002", "equipment_code": "CAT336", "type": "Excavator"},
        {"equipment_id": "EQ-003", "equipment_code": "KOMATSU", "type": "Dozer"},
        {"equipment_id": "EQ-004", "equipment_code": "VOLVO", "type": "Wheel Loader"},
        {"equipment_id": "EQ-005", "equipment_code": "JOHN", "type": "Backhoe"},
        {"equipment_id": "EQ-006", "equipment_code": "CASE", "type": "Skid Steer"},
        {"equipment_id": "EQ-007", "equipment_code": "BOBCAT", "type": "Skid Steer"},
        {"equipment_id": "EQ-008", "equipment_code": "COMPACTOR", "type": "Compactor"},
        {"equipment_id": "EQ-009", "equipment_code": "PAVER", "type": "Paver"},
        {"equipment_id": "EQ-010", "equipment_code": "ROLLER", "type": "Roller"},
    ]
    
    foremen = [
        {"foreman_id": "FM-001", "foreman_name": "John Smith"},
        {"foreman_id": "FM-002", "foreman_name": "Jane Doe"},
        {"foreman_id": "FM-003", "foreman_name": "Mike Johnson"},
    ]
    
    timecards = []
    base_date = datetime.now() - timedelta(days=30)
    
    for day_offset in range(30):
        work_date = base_date + timedelta(days=day_offset)
        
        for _ in range(random.randint(8, 12)):
            job = random.choice(jobs)
            equipment_item = random.choice(equipment)
            foreman = random.choice(foremen)
            
            hours = round(random.uniform(4, 10), 2)
            
            approval_delay = random.choice([0, 1, 2, 3, 5])
            submitted_at = work_date + timedelta(hours=random.randint(16, 22))
            approved_at = submitted_at + timedelta(days=approval_delay) if approval_delay > 0 else submitted_at
            
            timecard = {
                "timecard_id": f"TC-{work_date.strftime('%Y%m%d')}-{random.randint(1000, 9999)}",
                "job_id": job["job_id"],
                "equipment_id": equipment_item["equipment_id"],
                "foreman_id": foreman["foreman_id"],
                "work_date": work_date.strftime("%Y-%m-%d"),
                "hours": hours,
                "status": "APPROVED" if approval_delay == 0 else "PENDING" if approval_delay > 2 else "APPROVED",
                "submitted_at": submitted_at.isoformat(),
                "approved_at": approved_at.isoformat() if approval_delay > 0 else None,
            }
            timecards.append(timecard)
    
    return {
        "jobs": jobs,
        "equipment": equipment,
        "foremen": foremen,
        "timecards": timecards,
    }


def generate_mock_telematics():
    """Generate mock telematics GPS/engine hours data."""
    equipment = [
        {"equipment_id": "EQ-001", "device_id": "DEVICE-001"},
        {"equipment_id": "EQ-002", "device_id": "DEVICE-002"},
        {"equipment_id": "EQ-003", "device_id": "DEVICE-003"},
        {"equipment_id": "EQ-004", "device_id": "DEVICE-004"},
        {"equipment_id": "EQ-005", "device_id": "DEVICE-005"},
        {"equipment_id": "EQ-006", "device_id": "DEVICE-006"},
        {"equipment_id": "EQ-007", "device_id": "DEVICE-007"},
        {"equipment_id": "EQ-008", "device_id": "DEVICE-008"},
        {"equipment_id": "EQ-009", "device_id": "DEVICE-009"},
        {"equipment_id": "EQ-010", "device_id": "DEVICE-010"},
    ]
    
    readings = []
    base_date = datetime.now() - timedelta(days=30)
    
    for equipment_item in equipment:
        cumulative_hours = random.uniform(5000, 15000)
        
        for day_offset in range(30):
            work_date = base_date + timedelta(days=day_offset)
            
            daily_hours = round(random.uniform(3, 9), 2)
            cumulative_hours += daily_hours
            
            reading = {
                "equipment_id": equipment_item["equipment_id"],
                "device_id": equipment_item["device_id"],
                "date": work_date.strftime("%Y-%m-%d"),
                "engine_hours": round(cumulative_hours, 2),
                "daily_hours": daily_hours,
                "gps_active": random.choice([True, True, True, False]),
            }
            readings.append(reading)
    
    return {
        "equipment": equipment,
        "readings": readings,
    }


def generate_mock_inspections():
    """Generate mock daily inspection data."""
    equipment = [f"EQ-{i:03d}" for i in range(1, 11)]
    
    inspections = []
    base_date = datetime.now() - timedelta(days=30)
    
    for equipment_id in equipment:
        for day_offset in range(30):
            work_date = base_date + timedelta(days=day_offset)
            
            if random.random() > 0.15:
                hour_meter_start = round(random.uniform(1000, 5000), 1)
                hour_meter_end = round(hour_meter_start + random.uniform(2, 8), 1)
                
                inspection = {
                    "equipment_id": equipment_id,
                    "date": work_date.strftime("%Y-%m-%d"),
                    "hour_meter_start": hour_meter_start,
                    "hour_meter_end": hour_meter_end,
                    "meter_delta": round(hour_meter_end - hour_meter_start, 1),
                    "photo_count": random.randint(2, 8),
                    "issues_count": random.randint(0, 3),
                    "inspector_id": f"INS-{random.randint(1, 5):03d}",
                }
                inspections.append(inspection)
    
    return {
        "equipment": equipment,
        "inspections": inspections,
    }


def generate_mock_equipment360():
    """Generate mock Equipment360 meter readings."""
    equipment = [f"EQ-{i:03d}" for i in range(1, 11)]
    
    readings = []
    base_date = datetime.now() - timedelta(days=30)
    
    for equipment_id in equipment:
        cumulative_hours = random.uniform(5000, 15000)
        
        for day_offset in range(0, 30, 3):
            reading_date = base_date + timedelta(days=day_offset)
            
            cumulative_hours += random.uniform(15, 30)
            
            reading = {
                "equipment_id": equipment_id,
                "reading_date": reading_date.strftime("%Y-%m-%d"),
                "meter_type": "ENGINE_HOURS",
                "meter_value": round(cumulative_hours, 2),
            }
            readings.append(reading)
    
    return {
        "equipment": equipment,
        "readings": readings,
    }


def main():
    """Generate all mock data and save to fixtures."""
    fixtures_dir = Path(__file__).parent.parent / "data" / "fixtures"
    fixtures_dir.mkdir(parents=True, exist_ok=True)
    
    print("Generating mock HeavyJob data...")
    heavyjob_data = generate_mock_heavyjob()
    with open(fixtures_dir / "mock_heavyjob.json", "w") as f:
        json.dump(heavyjob_data, f, indent=2)
    print(f"  ✓ Generated {len(heavyjob_data['timecards'])} timecards")
    
    print("Generating mock telematics data...")
    telematics_data = generate_mock_telematics()
    with open(fixtures_dir / "mock_telematics.json", "w") as f:
        json.dump(telematics_data, f, indent=2)
    print(f"  ✓ Generated {len(telematics_data['readings'])} telematics readings")
    
    print("Generating mock inspections data...")
    inspections_data = generate_mock_inspections()
    with open(fixtures_dir / "mock_safety.json", "w") as f:
        json.dump(inspections_data, f, indent=2)
    print(f"  ✓ Generated {len(inspections_data['inspections'])} inspection records")
    
    print("Generating mock Equipment360 data...")
    equipment360_data = generate_mock_equipment360()
    with open(fixtures_dir / "mock_equipment360.json", "w") as f:
        json.dump(equipment360_data, f, indent=2)
    print(f"  ✓ Generated {len(equipment360_data['readings'])} Equipment360 readings")
    
    print(f"\n✓ All mock data generated in {fixtures_dir}")


if __name__ == "__main__":
    main()
