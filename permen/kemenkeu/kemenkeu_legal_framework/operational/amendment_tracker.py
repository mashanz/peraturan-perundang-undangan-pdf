#!/usr/bin/env python3
"""
KEMENKEU Amendment Tracking System - OPERATIONAL
Real-time monitoring and analysis of regulation amendments
"""

import requests
import psycopg2
import re
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import time
from bs4 import BeautifulSoup
import schedule
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class AmendmentTracker:
    """Operational amendment tracking and notification system"""
    
    def __init__(self, db_config: Dict, notification_config: Dict = None):
        self.db_config = db_config
        self.notification_config = notification_config or {}
        self.conn = None
        self.connect_db()
        
        # Indonesian amendment detection patterns
        self.amendment_patterns = {
            'partial': [
                r'mengubah\s+(?:beberapa\s+)?(?:ketentuan\s+)?(?:dalam\s+)?(?:Peraturan\s+Menteri\s+Keuangan|PMK)',
                r'merubah\s+(?:sebagian\s+)?(?:ketentuan\s+)?PMK',
                r'diubah\s+sebagai\s+berikut'
            ],
            'complete': [
                r'mengubah\s+(?:keseluruhan\s+)?(?:atas\s+)?(?:Peraturan\s+Menteri\s+Keuangan|PMK)',
                r'mengganti\s+(?:seluruhnya\s+)?PMK',
                r'diganti\s+(?:keseluruhan)?'
            ],
            'revocation': [
                r'mencabut\s+(?:dan\s+menyatakan\s+tidak\s+berlaku\s+)?(?:PMK|Peraturan\s+Menteri\s+Keuangan)',
                r'dicabut\s+(?:dan\s+dinyatakan\s+tidak\s+berlaku)',
                r'tidak\s+berlaku\s+lagi'
            ],
            'supersession': [
                r'menggantikan\s+(?:PMK|Peraturan\s+Menteri\s+Keuangan)',
                r'sebagai\s+pengganti\s+PMK',
                r'mengganti\s+PMK'
            ]
        }
        
        # Regulation ID extraction patterns
        self.id_patterns = [
            r'PMK[-.\s]?(\d+)[-/]PMK\.(\d+)[-/](\d{4})',
            r'Peraturan\s+Menteri\s+Keuangan\s+Nomor\s+(\d+)[-/]PMK\.(\d+)[-/](\d{4})',
            r'Nomor\s+(\d+)\s+Tahun\s+(\d{4})'
        ]
    
    def connect_db(self):
        """Connect to PostgreSQL database"""
        try:
            self.conn = psycopg2.connect(**self.db_config)
            print("✅ Amendment tracker database connection established")
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
    
    def fetch_recent_regulations(self, days_back: int = 7) -> List[Dict]:
        """Fetch recent regulations from official sources"""
        sources = [
            "https://peraturan.go.id/",
            "https://www.kemenkeu.go.id/informasi-publik/peraturan-perundang-undangan"
        ]
        
        recent_regulations = []
        
        for source in sources:
            try:
                # This is a simplified version - in production, implement proper scraping
                response = requests.get(source, timeout=10)
                if response.status_code == 200:
                    regulations = self._parse_regulation_list(response.text, source)
                    recent_regulations.extend(regulations)
                    print(f"✅ Fetched {len(regulations)} regulations from {source}")
                
            except Exception as e:
                print(f"❌ Error fetching from {source}: {e}")
        
        return recent_regulations
    
    def _parse_regulation_list(self, html_content: str, source: str) -> List[Dict]:
        """Parse regulation list from HTML content"""
        # Simplified parsing - in production, implement proper HTML parsing
        regulations = []
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # This would be customized for each source's HTML structure
        # For now, return sample data structure
        return []
    
    def detect_amendment_type(self, regulation_text: str) -> Optional[str]:
        """Detect amendment type from regulation text"""
        for amendment_type, patterns in self.amendment_patterns.items():
            for pattern in patterns:
                if re.search(pattern, regulation_text, re.IGNORECASE):
                    return amendment_type
        return None
    
    def extract_amended_regulation_id(self, text: str) -> Optional[str]:
        """Extract regulation ID being amended from text"""
        for pattern in self.id_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                if len(match.groups()) == 3:
                    number, series, year = match.groups()
                    return f"PMK-{number}/PMK.{series}/{year}"
                elif len(match.groups()) == 2:
                    number, year = match.groups()
                    return f"PMK-{number}/{year}"
        return None
    
    def process_new_regulation(self, regulation_data: Dict) -> Dict:
        """Process newly detected regulation for amendments"""
        result = {
            'regulation_id': regulation_data.get('id'),
            'is_amendment': False,
            'amendment_type': None,
            'amended_regulation': None,
            'impact_analysis': {},
            'notifications_sent': []
        }
        
        # Check if this is an amendment
        text = regulation_data.get('text', '') or regulation_data.get('title', '')
        amendment_type = self.detect_amendment_type(text)
        
        if amendment_type:
            result['is_amendment'] = True
            result['amendment_type'] = amendment_type
            
            # Extract original regulation ID
            amended_id = self.extract_amended_regulation_id(text)
            if amended_id:
                result['amended_regulation'] = amended_id
                
                # Store in database
                self._store_amendment(regulation_data['id'], amended_id, amendment_type, regulation_data)
                
                # Perform impact analysis
                result['impact_analysis'] = self.analyze_amendment_impact(amended_id, regulation_data['id'])
                
                # Send notifications
                result['notifications_sent'] = self.send_amendment_notifications(result)
        
        return result
    
    def _store_amendment(self, amending_id: str, original_id: str, amendment_type: str, regulation_data: Dict):
        """Store amendment in database"""
        try:
            with self.conn.cursor() as cur:
                # Insert or update regulation
                cur.execute("""
                    INSERT INTO regulations (id, type, number, year, series, title, date_enacted, date_effective, status, authority_level, issuing_authority)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO UPDATE SET
                        title = EXCLUDED.title,
                        date_enacted = EXCLUDED.date_enacted,
                        status = EXCLUDED.status
                """, (
                    amending_id, 'PMK', 
                    regulation_data.get('number', '0'),
                    regulation_data.get('year', datetime.now().year),
                    regulation_data.get('series', ''),
                    regulation_data.get('title', ''),
                    regulation_data.get('date_enacted', datetime.now().date()),
                    regulation_data.get('date_effective', datetime.now().date()),
                    'active', 4, 'Menteri Keuangan'
                ))
                
                # Insert amendment record
                cur.execute("""
                    INSERT INTO amendments (original_regulation_id, amending_regulation_id, amendment_type, 
                                          amendment_date, effective_date, description)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT DO NOTHING
                """, (
                    original_id, amending_id, amendment_type,
                    regulation_data.get('date_enacted', datetime.now().date()),
                    regulation_data.get('date_effective', datetime.now().date()),
                    f"Amendment detected: {amendment_type}"
                ))
                
                # Update status of original regulation
                if amendment_type == 'revocation':
                    cur.execute("UPDATE regulations SET status = 'revoked' WHERE id = %s", (original_id,))
                elif amendment_type in ['complete', 'supersession']:
                    cur.execute("UPDATE regulations SET status = 'superseded' WHERE id = %s", (original_id,))
                else:
                    cur.execute("UPDATE regulations SET status = 'amended' WHERE id = %s", (original_id,))
                
                self.conn.commit()
                print(f"✅ Amendment stored: {amending_id} -> {original_id} ({amendment_type})")
                
        except Exception as e:
            print(f"❌ Error storing amendment: {e}")
            self.conn.rollback()
    
    def analyze_amendment_impact(self, original_id: str, amending_id: str) -> Dict:
        """Analyze impact of amendment on systems and stakeholders"""
        impact_analysis = {
            'affected_systems': [],
            'stakeholder_notifications': [],
            'compliance_changes': [],
            'implementation_timeline': {}
        }
        
        try:
            with self.conn.cursor() as cur:
                # Find affected systems
                cur.execute("""
                    SELECT system_name, system_type, implementation_status, responsible_unit
                    FROM implementation_systems 
                    WHERE regulation_id = %s
                """, (original_id,))
                
                systems = cur.fetchall()
                for system_name, system_type, status, unit in systems:
                    impact_analysis['affected_systems'].append({
                        'system': system_name,
                        'type': system_type,
                        'current_status': status,
                        'responsible_unit': unit,
                        'action_required': 'update_required'
                    })
                
                # Find related regulations that might be affected
                cur.execute("""
                    SELECT citing_regulation_id, citation_type
                    FROM citations 
                    WHERE cited_regulation_id = %s
                """, (original_id,))
                
                related_regs = cur.fetchall()
                impact_analysis['related_regulations'] = len(related_regs)
                
        except Exception as e:
            print(f"❌ Error analyzing impact: {e}")
        
        return impact_analysis
    
    def send_amendment_notifications(self, amendment_data: Dict) -> List[str]:
        """Send notifications about amendments to stakeholders"""
        notifications_sent = []
        
        if not self.notification_config:
            return notifications_sent
        
        try:
            # Email notification
            if 'email' in self.notification_config:
                email_sent = self._send_email_notification(amendment_data)
                if email_sent:
                    notifications_sent.append('email')
            
            # System notifications (webhook, API calls, etc.)
            if 'webhook' in self.notification_config:
                webhook_sent = self._send_webhook_notification(amendment_data)
                if webhook_sent:
                    notifications_sent.append('webhook')
            
        except Exception as e:
            print(f"❌ Error sending notifications: {e}")
        
        return notifications_sent
    
    def _send_email_notification(self, amendment_data: Dict) -> bool:
        """Send email notification about amendment"""
        try:
            smtp_config = self.notification_config['email']
            
            msg = MIMEMultipart()
            msg['From'] = smtp_config['sender']
            msg['To'] = ', '.join(smtp_config['recipients'])
            msg['Subject'] = f"AMENDMENT ALERT: {amendment_data['regulation_id']}"
            
            body = f"""
KEMENKEU AMENDMENT NOTIFICATION

New Amendment Detected:
- Amending Regulation: {amendment_data['regulation_id']}
- Original Regulation: {amendment_data.get('amended_regulation', 'Unknown')}
- Amendment Type: {amendment_data.get('amendment_type', 'Unknown')}

Impact Summary:
- Affected Systems: {len(amendment_data.get('impact_analysis', {}).get('affected_systems', []))}
- Related Regulations: {amendment_data.get('impact_analysis', {}).get('related_regulations', 0)}

Immediate Actions Required:
1. Review amendment details
2. Update affected systems
3. Notify relevant stakeholders
4. Update compliance procedures

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            with smtplib.SMTP(smtp_config['server'], smtp_config['port']) as server:
                server.starttls()
                server.login(smtp_config['username'], smtp_config['password'])
                server.send_message(msg)
            
            return True
            
        except Exception as e:
            print(f"❌ Email notification failed: {e}")
            return False
    
    def _send_webhook_notification(self, amendment_data: Dict) -> bool:
        """Send webhook notification"""
        try:
            webhook_config = self.notification_config['webhook']
            
            payload = {
                'event_type': 'amendment_detected',
                'timestamp': datetime.now().isoformat(),
                'data': amendment_data
            }
            
            response = requests.post(
                webhook_config['url'],
                json=payload,
                headers=webhook_config.get('headers', {}),
                timeout=10
            )
            
            return response.status_code == 200
            
        except Exception as e:
            print(f"❌ Webhook notification failed: {e}")
            return False
    
    def generate_amendment_report(self, days: int = 30) -> Dict:
        """Generate amendment activity report"""
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days)
        
        report = {
            'period': f"{start_date} to {end_date}",
            'summary': {},
            'amendments': [],
            'trends': {}
        }
        
        try:
            with self.conn.cursor() as cur:
                # Get amendment summary
                cur.execute("""
                    SELECT amendment_type, COUNT(*) as count
                    FROM amendments 
                    WHERE amendment_date >= %s AND amendment_date <= %s
                    GROUP BY amendment_type
                """, (start_date, end_date))
                
                summary = dict(cur.fetchall())
                report['summary'] = summary
                
                # Get detailed amendments
                cur.execute("""
                    SELECT a.original_regulation_id, a.amending_regulation_id, a.amendment_type, 
                           a.amendment_date, r1.title as original_title, r2.title as amending_title
                    FROM amendments a
                    JOIN regulations r1 ON a.original_regulation_id = r1.id
                    JOIN regulations r2 ON a.amending_regulation_id = r2.id
                    WHERE a.amendment_date >= %s AND a.amendment_date <= %s
                    ORDER BY a.amendment_date DESC
                """, (start_date, end_date))
                
                amendments = []
                for row in cur.fetchall():
                    amendments.append({
                        'original_regulation': row[0],
                        'amending_regulation': row[1],
                        'type': row[2],
                        'date': row[3].isoformat(),
                        'original_title': row[4],
                        'amending_title': row[5]
                    })
                
                report['amendments'] = amendments
                
        except Exception as e:
            print(f"❌ Error generating report: {e}")
        
        return report
    
    def run_daily_scan(self):
        """Run daily scan for new regulations and amendments"""
        print(f"🔍 Starting daily amendment scan at {datetime.now()}")
        
        # Fetch recent regulations
        recent_regs = self.fetch_recent_regulations(days_back=2)
        
        amendments_found = 0
        for reg_data in recent_regs:
            result = self.process_new_regulation(reg_data)
            if result['is_amendment']:
                amendments_found += 1
        
        print(f"✅ Daily scan completed: {amendments_found} amendments found")
        
        # Generate and store daily report
        report = self.generate_amendment_report(days=1)
        if report['amendments']:
            self._store_daily_report(report)
    
    def _store_daily_report(self, report: Dict):
        """Store daily report for future reference"""
        report_file = f"daily_amendment_report_{datetime.now().strftime('%Y%m%d')}.json"
        try:
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False, default=str)
            print(f"📄 Daily report saved: {report_file}")
        except Exception as e:
            print(f"❌ Error saving report: {e}")

# SCHEDULED OPERATIONS
def setup_scheduled_monitoring(tracker: AmendmentTracker):
    """Setup scheduled monitoring tasks"""
    
    # Daily scan at 6 AM
    schedule.every().day.at("06:00").do(tracker.run_daily_scan)
    
    # Weekly comprehensive report on Monday at 9 AM
    schedule.every().monday.at("09:00").do(lambda: tracker.generate_amendment_report(days=7))
    
    print("📅 Scheduled monitoring configured:")
    print("- Daily scan: 06:00")
    print("- Weekly report: Monday 09:00")

# COMMAND LINE INTERFACE
if __name__ == "__main__":
    import sys
    
    DB_CONFIG = {
        'host': 'localhost',
        'database': 'kemenkeu_legal',
        'user': 'postgres',
        'password': 'password'
    }
    
    NOTIFICATION_CONFIG = {
        'email': {
            'server': 'smtp.gmail.com',
            'port': 587,
            'sender': 'legal-system@kemenkeu.go.id',
            'recipients': ['legal-team@kemenkeu.go.id', 'compliance@kemenkeu.go.id'],
            'username': 'legal-system@kemenkeu.go.id',
            'password': 'app-password'
        }
    }
    
    tracker = AmendmentTracker(DB_CONFIG, NOTIFICATION_CONFIG)
    
    if len(sys.argv) < 2:
        print("Usage: python amendment_tracker.py <command>")
        print("Commands: scan, monitor, report")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "scan":
        tracker.run_daily_scan()
        
    elif command == "monitor":
        setup_scheduled_monitoring(tracker)
        print("🔄 Starting scheduled monitoring...")
        while True:
            schedule.run_pending()
            time.sleep(60)
            
    elif command == "report":
        days = int(sys.argv[2]) if len(sys.argv) > 2 else 30
        report = tracker.generate_amendment_report(days)
        print(json.dumps(report, indent=2, ensure_ascii=False, default=str))
        
    else:
        print("Invalid command")