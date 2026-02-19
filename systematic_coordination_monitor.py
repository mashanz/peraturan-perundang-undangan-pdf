#!/usr/bin/env python3
"""
Systematic Batch Processing Coordinator Monitor
Real-time tracking of 4 systematic collection agents
"""

import os
import json
import time
from datetime import datetime
from pathlib import Path
import glob

class SystematicCoordinationMonitor:
    def __init__(self, repo_path="/root/.openclaw/peraturan-perundang-undangan-pdf"):
        self.repo_path = Path(repo_path)
        self.start_time = datetime.now()
        
        # Agent directory mappings
        self.agent_dirs = {
            'finance': {
                'name': 'Finance Agent (PMK)',
                'patterns': ['pmk-*.pdf'],
                'directories': ['.']
            },
            'ministerial': {
                'name': 'Ministerial Agent (PERMEN)',
                'patterns': ['permen/*/*.pdf', '*pmperin*.pdf', '*permen*.pdf'],
                'directories': ['permen', 'permen/*']
            },
            'constitutional': {
                'name': 'Constitutional Agent (UU/PP/PERPRES)',
                'patterns': ['uu/*.pdf', 'pp/*.pdf', 'perpres/*.pdf', 'constitutional/*.pdf', '*uu*.pdf', '*pp*.pdf', '*perpres*.pdf'],
                'directories': ['uu', 'pp', 'perpres', 'constitutional']
            },
            'regional': {
                'name': 'Regional Agent (PERDA)',
                'patterns': ['perda/*/*.pdf', '*perda*.pdf'],
                'directories': ['perda', 'perda/*']
            }
        }
        
        # Initialize tracking data
        self.agent_stats = {}
        self.last_check = {}
        self.hourly_rates = {}
        
    def count_files_by_agent(self):
        """Count files for each systematic collection agent"""
        os.chdir(self.repo_path)
        results = {}
        
        for agent_id, config in self.agent_dirs.items():
            total_files = 0
            total_size = 0
            new_files = 0
            
            # Count files matching patterns
            for pattern in config['patterns']:
                files = glob.glob(pattern, recursive=True)
                for file_path in files:
                    if os.path.isfile(file_path) and file_path.endswith('.pdf'):
                        try:
                            size = os.path.getsize(file_path)
                            total_files += 1
                            total_size += size
                            
                            # Check if file is new (created in last hour)
                            mtime = os.path.getmtime(file_path)
                            if time.time() - mtime < 3600:  # Last hour
                                new_files += 1
                        except:
                            continue
            
            results[agent_id] = {
                'name': config['name'],
                'total_files': total_files,
                'total_size_mb': total_size / (1024 * 1024),
                'new_files_last_hour': new_files,
                'timestamp': datetime.now()
            }
            
        return results
    
    def calculate_hourly_rates(self, current_stats):
        """Calculate files per hour for each agent"""
        elapsed_hours = (datetime.now() - self.start_time).total_seconds() / 3600
        
        for agent_id, stats in current_stats.items():
            if elapsed_hours > 0:
                files_per_hour = stats['total_files'] / elapsed_hours
                self.hourly_rates[agent_id] = files_per_hour
            else:
                self.hourly_rates[agent_id] = 0
    
    def get_git_status(self):
        """Get current git status and staging info"""
        try:
            import subprocess
            
            # Get untracked files
            result = subprocess.run(['git', 'status', '--porcelain'], 
                                  capture_output=True, text=True, cwd=self.repo_path)
            
            untracked_pdfs = []
            staged_files = 0
            
            for line in result.stdout.strip().split('\n'):
                if line and line.endswith('.pdf'):
                    status = line[:2].strip()
                    filename = line[3:]
                    
                    if status == '??':  # Untracked
                        try:
                            size = os.path.getsize(self.repo_path / filename)
                            untracked_pdfs.append({
                                'filename': filename,
                                'size_mb': size / (1024 * 1024)
                            })
                        except:
                            continue
                    elif status in ['A', 'M']:  # Staged
                        staged_files += 1
            
            return {
                'untracked_pdfs': len(untracked_pdfs),
                'untracked_size_mb': sum(f['size_mb'] for f in untracked_pdfs),
                'staged_files': staged_files,
                'pending_files': untracked_pdfs[:10]  # Show first 10
            }
        except Exception as e:
            return {'error': str(e)}
    
    def generate_coordination_report(self):
        """Generate comprehensive systematic coordination report"""
        current_stats = self.count_files_by_agent()
        self.calculate_hourly_rates(current_stats)
        git_status = self.get_git_status()
        
        elapsed_time = datetime.now() - self.start_time
        elapsed_minutes = elapsed_time.total_seconds() / 60
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'runtime_minutes': elapsed_minutes,
            'systematic_agents': {},
            'git_status': git_status,
            'coordination_metrics': {
                'total_files_across_agents': 0,
                'total_size_mb': 0,
                'combined_files_per_hour': 0,
                'batch_processing_status': 'active'
            }
        }
        
        # Process each agent
        total_files = 0
        total_size = 0
        combined_rate = 0
        
        for agent_id, stats in current_stats.items():
            agent_report = {
                'name': stats['name'],
                'total_files': stats['total_files'],
                'total_size_mb': round(stats['total_size_mb'], 2),
                'new_files_last_hour': stats['new_files_last_hour'],
                'files_per_hour_rate': round(self.hourly_rates.get(agent_id, 0), 1),
                'status': 'active' if stats['new_files_last_hour'] > 0 else 'monitoring'
            }
            
            report['systematic_agents'][agent_id] = agent_report
            
            total_files += stats['total_files']
            total_size += stats['total_size_mb']
            combined_rate += self.hourly_rates.get(agent_id, 0)
        
        # Update coordination metrics
        report['coordination_metrics']['total_files_across_agents'] = total_files
        report['coordination_metrics']['total_size_mb'] = round(total_size, 2)
        report['coordination_metrics']['combined_files_per_hour'] = round(combined_rate, 1)
        
        return report
    
    def display_live_dashboard(self):
        """Display live coordination dashboard"""
        while True:
            try:
                report = self.generate_coordination_report()
                
                # Clear screen
                os.system('clear')
                
                print("=" * 80)
                print("🎯 SYSTEMATIC BATCH PROCESSING COORDINATION DASHBOARD")
                print("=" * 80)
                print(f"⏱️  Runtime: {report['runtime_minutes']:.1f} minutes")
                print(f"📊 Combined Rate: {report['coordination_metrics']['combined_files_per_hour']:.1f} files/hour")
                print(f"📄 Total Files: {report['coordination_metrics']['total_files_across_agents']:,}")
                print(f"💾 Total Size: {report['coordination_metrics']['total_size_mb']:.1f}MB")
                print()
                
                # Agent status
                print("🤖 SYSTEMATIC COLLECTION AGENTS:")
                for agent_id, agent in report['systematic_agents'].items():
                    status_icon = "🟢" if agent['status'] == 'active' else "🟡"
                    print(f"{status_icon} {agent['name']}")
                    print(f"   ├── Files: {agent['total_files']:,} ({agent['total_size_mb']:.1f}MB)")
                    print(f"   ├── New/Hour: {agent['new_files_last_hour']} files")
                    print(f"   └── Rate: {agent['files_per_hour_rate']:.1f} files/hour")
                    print()
                
                # Git status
                git = report['git_status']
                if 'error' not in git:
                    print("📦 BATCH PROCESSING STATUS:")
                    print(f"├── Untracked PDFs: {git['untracked_pdfs']} files ({git['untracked_size_mb']:.1f}MB)")
                    print(f"├── Staged Files: {git['staged_files']}")
                    print(f"└── Threshold: {'✅ READY' if git['untracked_size_mb'] >= 5 else '⏳ WAITING'} (5MB minimum)")
                    print()
                    
                    if git['pending_files']:
                        print("📋 PENDING FILES (sample):")
                        for file in git['pending_files'][:5]:
                            print(f"├── {file['filename']} ({file['size_mb']:.1f}MB)")
                        if len(git['pending_files']) > 5:
                            print(f"└── ... and {len(git['pending_files']) - 5} more")
                        print()
                
                print("🚀 COORDINATION ACTIVE - Press Ctrl+C to stop")
                print("=" * 80)
                
                # Wait 30 seconds before next update
                time.sleep(30)
                
            except KeyboardInterrupt:
                print("\n🛑 Systematic Coordination Monitor stopped")
                break
            except Exception as e:
                print(f"❌ Monitor error: {e}")
                time.sleep(10)

def main():
    monitor = SystematicCoordinationMonitor()
    
    # Generate initial report
    print("🎯 SYSTEMATIC BATCH PROCESSING COORDINATOR")
    print("Initializing multi-agent coordination monitoring...")
    print()
    
    # Start live dashboard
    monitor.display_live_dashboard()

if __name__ == "__main__":
    main()