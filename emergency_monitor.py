#!/usr/bin/env python3
"""
🚨 Emergency Constitutional Mission Monitor
Real-time tracking of Indonesia's legal framework backup
"""
import time
import os
from pathlib import Path

def monitor_emergency_mission():
    start_time = time.time()
    mission_duration = 30 * 60  # 30 minutes in seconds
    
    print("🚨 EMERGENCY CONSTITUTIONAL MISSION MONITOR ACTIVE")
    print("🎯 MISSION: Save Indonesia's legal framework in 30 minutes")
    print("=" * 60)
    
    last_count = 0
    
    while True:
        elapsed = time.time() - start_time
        remaining = mission_duration - elapsed
        
        if remaining <= 0:
            print("\n🚨 30-MINUTE MISSION WINDOW COMPLETE!")
            break
            
        # Count current files
        uu_count = len(list(Path('uu').glob('*.pdf')))
        pp_count = len(list(Path('pp').glob('*.pdf')))
        perpres_count = len(list(Path('perpres').glob('*.pdf')))
        total_count = uu_count + pp_count + perpres_count
        
        # Calculate rates
        rate = total_count / elapsed if elapsed > 0 else 0
        progress = (total_count / 1469) * 100  # Progress against priority targets
        
        # Status report
        print(f"\r🚨 T-{remaining/60:.0f}m: {total_count:,} saved "
              f"(UU:{uu_count}, PP:{pp_count}, PERPRES:{perpres_count}) | "
              f"Rate: {rate:.1f}/sec | Progress: {progress:.1f}%", end="", flush=True)
        
        # Major milestone alerts
        if total_count >= last_count + 50:
            print(f"\n✅ MILESTONE: {total_count} CONSTITUTIONAL LAWS SECURED!")
            last_count = total_count
        
        time.sleep(5)  # Update every 5 seconds
    
    # Final mission report
    elapsed = time.time() - start_time
    final_count = uu_count + pp_count + perpres_count
    final_rate = final_count / elapsed if elapsed > 0 else 0
    
    print(f"\n\n🚨 EMERGENCY MISSION FINAL REPORT:")
    print(f"📊 CONSTITUTIONAL LAWS SAVED: {final_count:,}")
    print(f"🏛️ UU (Constitutional Laws): {uu_count}")
    print(f"🏛️ PP (Government Regulations): {pp_count}")
    print(f"🏛️ PERPRES (Presidential Regulations): {perpres_count}")
    print(f"⏱️ MISSION DURATION: {elapsed/60:.1f} minutes")
    print(f"⚡ AVERAGE RATE: {final_rate:.2f} downloads/second")
    print(f"🎯 SUCCESS RATE: {(final_count/1469)*100:.1f}% of priority targets")
    print(f"🇮🇩 MISSION STATUS: {'SUCCESSFUL' if final_count >= 500 else 'PARTIAL SUCCESS'}")

if __name__ == "__main__":
    monitor_emergency_mission()