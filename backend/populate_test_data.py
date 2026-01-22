# populate_test_data.py
import sys
import os
import random
from datetime import datetime, timedelta

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionLocal
from app.models.user import User, UserRole
from app.models.hospital import Hospital
from app.models.patient import PatientEncounter, Setting
from app.models.recommendation import Recommendation
from app.models.analytics import BloodProductCost
from app.models.audit import AuditLog

def populate_data():
    db = SessionLocal()
    
    try:
        print("Starting data population...")
        
        # Get hospital
        hospital = db.query(Hospital).first()
        if not hospital:
            print("❌ No hospital found. Please create a hospital first.")
            return
        
        print(f"✅ Found hospital: {hospital.name} (ID: {hospital.id})")
        
        # Get a user
        user = db.query(User).first()
        if not user:
            print("❌ No user found. Please create a user first.")
            return
        
        print(f"✅ Found user: {user.email} (ID: {user.id})")
        
        # Create blood product costs (required for ROI calculation)
        print("\nSetting up blood product costs...")
        components = ['RBC', 'FFP', 'Platelets', 'Cryoprecipitate']
        for component in components:
            cost = db.query(BloodProductCost).filter(
                BloodProductCost.hospital_id == hospital.id,
                BloodProductCost.component_type == component
            ).first()
            
            if not cost:
                cost = BloodProductCost(
                    hospital_id=hospital.id,
                    component_type=component,
                    unit_cost_bdt=random.randint(2000, 5000),
                    units_per_bag=1,
                    is_active=True
                )
                db.add(cost)
                print(f"  ✅ Created cost for {component}: {cost.unit_cost_bdt} BDT")
            else:
                print(f"  ℹ️  Cost for {component} already exists: {cost.unit_cost_bdt} BDT")
        
        db.commit()
        
        # Create sample patient encounters (last 6 months)
        print("\nCreating sample patient encounters...")
        encounter_count = 0
        recommendation_count = 0
        
        for i in range(30):
            days_ago = random.randint(0, 30)
            encounter_date = datetime.now() - timedelta(days=days_ago)
            
            encounter = PatientEncounter(
                hospital_id=hospital.id,
                patient_id=f"PAT{random.randint(1000, 9999)}",
                department=random.choice(['ICU', 'Ward', 'Surgery', 'ER', 'Clinic']),
                age_years=random.randint(20, 80),
                sex=random.choice(['M', 'F']),
                weight_kg=random.randint(50, 90),
                setting=random.choice(list(Setting)),
                active_bleeding=random.choice([True, False]),
                hemodynamic_instability=random.choice([True, False]),
                hb_gdl=random.uniform(6.0, 12.0),
                platelets_x109l=random.uniform(50, 200),
                inr=random.uniform(1.0, 2.5),
                fibrinogen_mgdl=random.uniform(150, 400),
                history_flags={"cad": random.choice([True, False]), 
                              "liver_disease": random.choice([True, False])},
                created_by=user.id,
                created_at=encounter_date,
                is_active=True
            )
            db.add(encounter)
            db.flush()  # Get the ID
            
            encounter_count += 1
            
            # Create recommendation for some encounters (70% chance)
            if random.random() < 0.7:
                component = random.choice(['RBC', 'FFP', 'Platelets', 'Cryoprecipitate', None])
                
                recommendation = Recommendation(
                    encounter_id=encounter.id,
                    component=component,
                    dose_text=f"{random.randint(1, 3)} unit{'s' if random.randint(1, 3) > 1 else ''}",
                    units=random.randint(1, 3),
                    volume_ml=350 if component == 'RBC' else random.choice([200, 250, 300]),
                    expected_increment=f"Expected Hb increase: {random.uniform(0.5, 1.5):.1f} g/dL" if component == 'RBC' else "As per protocol",
                    recheck_plan="Recheck CBC in 24 hours",
                    why=["Low hemoglobin per guidelines"] if component == 'RBC' else ["As per coagulation guidelines"],
                    warnings=[],
                    references=["NICE Guideline NG24", "AABB Guidelines"],
                    rule_ids=[f"rule_{random.randint(100, 999):03d}"],
                    rule_version="1.0.0",
                    created_at=encounter_date
                )
                db.add(recommendation)
                recommendation_count += 1
        
        db.commit()
        print(f"\n✅ Created {encounter_count} sample encounters")
        print(f"✅ Created {recommendation_count} recommendations")
        
        # Create some audit logs for overrides (20% of recommendations)
        print("\nCreating audit logs for overrides...")
        recommendations = db.query(Recommendation).limit(10).all()
        override_count = 0
        
        for rec in recommendations:
            if random.random() < 0.2:  # 20% override rate
                audit_log = AuditLog(
                    encounter_id=rec.encounter_id,
                    recommendation_id=rec.id,
                    action="override",
                    user_id=user.id,
                    override_reason=random.choice([
                        "Clinical judgement",
                        "Patient preference",
                        "Component not available",
                        "Different protocol followed"
                    ]),
                    override_component=rec.component,
                    rule_version="1.0.0",
                    created_at=rec.created_at + timedelta(hours=1)
                )
                db.add(audit_log)
                override_count += 1
        
        db.commit()
        print(f"✅ Created {override_count} audit logs for overrides")
        
        # Final summary
        print("\n" + "="*50)
        print("📊 DATA POPULATION COMPLETE")
        print("="*50)
        total_encounters = db.query(PatientEncounter).count()
        total_recommendations = db.query(Recommendation).count()
        total_audit_logs = db.query(AuditLog).count()
        
        print(f"Total encounters in database: {total_encounters}")
        print(f"Total recommendations in database: {total_recommendations}")
        print(f"Total audit logs in database: {total_audit_logs}")
        print(f"Override rate: {(override_count / recommendation_count * 100):.1f}%" if recommendation_count > 0 else "Override rate: N/A")
        print("\n✅ You can now test the analytics dashboard with real data!")
        
    except Exception as e:
        db.rollback()
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    populate_data()