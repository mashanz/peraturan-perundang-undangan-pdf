#!/usr/bin/env python3
"""
KEMENKEU Legal Framework Dashboard - OPERATIONAL COMMAND CENTER
Real-time dashboard for legal framework monitoring and analysis
"""

import psycopg2
import json
from datetime import datetime, timedelta
from typing import Dict, List
import pandas as pd
from citation_network_analyzer import LegalCitationAnalyzer
from amendment_tracker import AmendmentTracker
from implementation_matrix import ImplementationMatrix

class LegalFrameworkDashboard:
    """Central operational dashboard for KEMENKEU legal framework"""
    
    def __init__(self, db_config: Dict):
        self.db_config = db_config
        self.conn = None
        self.connect_db()
        
        # Initialize component systems
        self.citation_analyzer = LegalCitationAnalyzer(db_config)
        self.amendment_tracker = AmendmentTracker(db_config)
        self.implementation_matrix = ImplementationMatrix(db_config)
        
    def connect_db(self):
        """Connect to PostgreSQL database"""
        try:
            self.conn = psycopg2.connect(**self.db_config)
            print("✅ Dashboard database connection established")
        except Exception as e:
            print(f"❌ Dashboard database connection failed: {e}")
    
    def get_system_overview(self) -> Dict:
        """Get comprehensive system overview"""
        overview = {
            'timestamp': datetime.now().isoformat(),
            'regulation_statistics': self._get_regulation_stats(),
            'citation_network': self._get_network_stats(),
            'amendment_activity': self._get_amendment_stats(),
            'implementation_status': self._get_implementation_stats(),
            'compliance_summary': self._get_compliance_summary(),
            'alerts': self._get_system_alerts()
        }
        
        return overview
    
    def _get_regulation_stats(self) -> Dict:
        """Get regulation statistics"""
        try:
            with self.conn.cursor() as cur:
                # Total regulations by type and status
                cur.execute("""
                    SELECT type, status, COUNT(*) as count
                    FROM regulations 
                    GROUP BY type, status
                    ORDER BY type, status
                """)
                
                stats = {}
                for reg_type, status, count in cur.fetchall():
                    if reg_type not in stats:
                        stats[reg_type] = {}
                    stats[reg_type][status] = count
                
                # Recent activity (last 30 days)
                cur.execute("""
                    SELECT COUNT(*) FROM regulations 
                    WHERE created_at >= %s
                """, (datetime.now() - timedelta(days=30),))
                
                recent_count = cur.fetchone()[0]
                
                # PMK by series
                cur.execute("""
                    SELECT series, COUNT(*) as count
                    FROM regulations 
                    WHERE type = 'PMK' AND status = 'active'
                    GROUP BY series
                    ORDER BY count DESC
                """)
                
                pmk_series = dict(cur.fetchall())
                
                return {
                    'by_type_status': stats,
                    'recent_additions_30d': recent_count,
                    'pmk_by_series': pmk_series,
                    'total_active_pmk': sum(pmk_series.values())
                }
                
        except Exception as e:
            return {'error': str(e)}
    
    def _get_network_stats(self) -> Dict:
        """Get citation network statistics"""
        try:
            self.citation_analyzer.build_citation_network()
            
            with self.conn.cursor() as cur:
                # Citation types
                cur.execute("""
                    SELECT citation_type, COUNT(*) as count
                    FROM citations
                    GROUP BY citation_type
                    ORDER BY count DESC
                """)
                
                citation_types = dict(cur.fetchall())
                
                # Most cited regulations
                cur.execute("""
                    SELECT c.cited_regulation_id, r.title, COUNT(*) as citation_count
                    FROM citations c
                    JOIN regulations r ON c.cited_regulation_id = r.id
                    GROUP BY c.cited_regulation_id, r.title
                    ORDER BY citation_count DESC
                    LIMIT 10
                """)
                
                most_cited = [
                    {'regulation_id': row[0], 'title': row[1][:100], 'citation_count': row[2]}
                    for row in cur.fetchall()
                ]
                
                # Network metrics
                graph = self.citation_analyzer.graph
                network_metrics = {
                    'total_nodes': len(graph.nodes),
                    'total_edges': len(graph.edges),
                    'network_density': len(graph.edges) / (len(graph.nodes) * (len(graph.nodes) - 1)) if len(graph.nodes) > 1 else 0
                }
                
                return {
                    'citation_types': citation_types,
                    'most_cited_regulations': most_cited,
                    'network_metrics': network_metrics,
                    'circular_references': len(self.citation_analyzer.detect_circular_references())
                }
                
        except Exception as e:
            return {'error': str(e)}
    
    def _get_amendment_stats(self) -> Dict:
        """Get amendment activity statistics"""
        try:
            with self.conn.cursor() as cur:
                # Amendments by type (last 12 months)
                cur.execute("""
                    SELECT amendment_type, COUNT(*) as count
                    FROM amendments
                    WHERE amendment_date >= %s
                    GROUP BY amendment_type
                    ORDER BY count DESC
                """, (datetime.now().date() - timedelta(days=365),))
                
                amendment_types = dict(cur.fetchall())
                
                # Recent amendments (last 30 days)
                cur.execute("""
                    SELECT a.original_regulation_id, a.amending_regulation_id, a.amendment_type, 
                           a.amendment_date, r1.title as original_title
                    FROM amendments a
                    JOIN regulations r1 ON a.original_regulation_id = r1.id
                    WHERE a.amendment_date >= %s
                    ORDER BY a.amendment_date DESC
                    LIMIT 10
                """, (datetime.now().date() - timedelta(days=30),))
                
                recent_amendments = [
                    {
                        'original_regulation': row[0],
                        'amending_regulation': row[1],
                        'type': row[2],
                        'date': row[3].isoformat(),
                        'original_title': row[4][:100]
                    }
                    for row in cur.fetchall()
                ]
                
                # Amendment trend (monthly for last 12 months)
                cur.execute("""
                    SELECT DATE_TRUNC('month', amendment_date) as month, COUNT(*) as count
                    FROM amendments
                    WHERE amendment_date >= %s
                    GROUP BY month
                    ORDER BY month
                """, (datetime.now().date() - timedelta(days=365),))
                
                monthly_trend = [
                    {'month': row[0].strftime('%Y-%m'), 'count': row[1]}
                    for row in cur.fetchall()
                ]
                
                return {
                    'amendment_types_12m': amendment_types,
                    'recent_amendments_30d': recent_amendments,
                    'monthly_trend': monthly_trend,
                    'total_amendments_12m': sum(amendment_types.values())
                }
                
        except Exception as e:
            return {'error': str(e)}
    
    def _get_implementation_stats(self) -> Dict:
        """Get implementation status statistics"""
        try:
            with self.conn.cursor() as cur:
                # Implementation by system
                cur.execute("""
                    SELECT system_name, implementation_status, COUNT(*) as count
                    FROM implementation_systems
                    GROUP BY system_name, implementation_status
                    ORDER BY system_name, implementation_status
                """)
                
                system_status = {}
                for system, status, count in cur.fetchall():
                    if system not in system_status:
                        system_status[system] = {}
                    system_status[system][status] = count
                
                # Overall implementation progress
                cur.execute("""
                    SELECT 
                        COUNT(*) as total_implementations,
                        COUNT(CASE WHEN implementation_status = 'completed' THEN 1 END) as completed,
                        COUNT(CASE WHEN implementation_status = 'in_progress' THEN 1 END) as in_progress,
                        COUNT(CASE WHEN implementation_status = 'planned' THEN 1 END) as planned
                    FROM implementation_systems
                """)
                
                overall = cur.fetchone()
                overall_stats = {
                    'total': overall[0],
                    'completed': overall[1],
                    'in_progress': overall[2],
                    'planned': overall[3],
                    'completion_rate': round(overall[1] / overall[0] * 100, 1) if overall[0] > 0 else 0
                }
                
                # Overdue implementations
                cur.execute("""
                    SELECT r.id, r.title, i.system_name, i.go_live_date
                    FROM implementation_systems i
                    JOIN regulations r ON i.regulation_id = r.id
                    WHERE i.implementation_status != 'completed' 
                      AND i.go_live_date < %s
                    ORDER BY i.go_live_date
                    LIMIT 10
                """, (datetime.now().date(),))
                
                overdue = [
                    {
                        'regulation_id': row[0],
                        'title': row[1][:100],
                        'system': row[2],
                        'due_date': row[3].isoformat() if row[3] else None
                    }
                    for row in cur.fetchall()
                ]
                
                return {
                    'by_system_status': system_status,
                    'overall_progress': overall_stats,
                    'overdue_implementations': overdue
                }
                
        except Exception as e:
            return {'error': str(e)}
    
    def _get_compliance_summary(self) -> Dict:
        """Get compliance summary"""
        try:
            with self.conn.cursor() as cur:
                # International compliance
                cur.execute("""
                    SELECT alignment_status, COUNT(*) as count
                    FROM international_alignments
                    GROUP BY alignment_status
                    ORDER BY count DESC
                """)
                
                international_compliance = dict(cur.fetchall())
                
                # Legal hierarchy compliance
                compliance_report = self.citation_analyzer.generate_compliance_report()
                
                return {
                    'international_alignment': international_compliance,
                    'legal_hierarchy': compliance_report['validation_summary'],
                    'circular_references': len(compliance_report['circular_references']),
                    'total_violations': len(compliance_report['violations'])
                }
                
        except Exception as e:
            return {'error': str(e)}
    
    def _get_system_alerts(self) -> List[Dict]:
        """Get system alerts and notifications"""
        alerts = []
        
        try:
            with self.conn.cursor() as cur:
                # Overdue implementations
                cur.execute("""
                    SELECT COUNT(*) FROM implementation_systems
                    WHERE implementation_status != 'completed' 
                      AND go_live_date < %s
                """, (datetime.now().date(),))
                
                overdue_count = cur.fetchone()[0]
                if overdue_count > 0:
                    alerts.append({
                        'type': 'warning',
                        'category': 'implementation',
                        'message': f'{overdue_count} implementations are overdue',
                        'priority': 'high',
                        'timestamp': datetime.now().isoformat()
                    })
                
                # Recent amendments requiring attention
                cur.execute("""
                    SELECT COUNT(*) FROM amendments
                    WHERE amendment_date >= %s
                """, (datetime.now().date() - timedelta(days=7),))
                
                recent_amendments = cur.fetchone()[0]
                if recent_amendments > 0:
                    alerts.append({
                        'type': 'info',
                        'category': 'amendments',
                        'message': f'{recent_amendments} new amendments in the last 7 days',
                        'priority': 'medium',
                        'timestamp': datetime.now().isoformat()
                    })
                
                # Legal hierarchy violations
                compliance_report = self.citation_analyzer.generate_compliance_report()
                violations = compliance_report['validation_summary']['invalid_regulations']
                if violations > 0:
                    alerts.append({
                        'type': 'error',
                        'category': 'compliance',
                        'message': f'{violations} regulations have legal hierarchy violations',
                        'priority': 'high',
                        'timestamp': datetime.now().isoformat()
                    })
                
        except Exception as e:
            alerts.append({
                'type': 'error',
                'category': 'system',
                'message': f'Error generating alerts: {str(e)}',
                'priority': 'high',
                'timestamp': datetime.now().isoformat()
            })
        
        return alerts
    
    def generate_daily_report(self) -> str:
        """Generate comprehensive daily report"""
        overview = self.get_system_overview()
        
        report = f"""
════════════════════════════════════════════════════════════════
KEMENKEU LEGAL FRAMEWORK - DAILY OPERATIONAL REPORT
Generated: {overview['timestamp']}
════════════════════════════════════════════════════════════════

📊 REGULATION STATISTICS
────────────────────────
• Active PMK Regulations: {overview['regulation_statistics']['total_active_pmk']}
• New Regulations (30d): {overview['regulation_statistics']['recent_additions_30d']}
• Top PMK Series: {', '.join([f"{k}({v})" for k, v in list(overview['regulation_statistics']['pmk_by_series'].items())[:3]])}

🔗 CITATION NETWORK
─────────────────────
• Total Network Size: {overview['citation_network']['network_metrics']['total_nodes']} regulations, {overview['citation_network']['network_metrics']['total_edges']} citations
• Network Density: {overview['citation_network']['network_metrics']['network_density']:.3f}
• Circular References: {overview['citation_network']['circular_references']} detected

📋 AMENDMENT ACTIVITY
───────────────────────
• Total Amendments (12m): {overview['amendment_activity']['total_amendments_12m']}
• Recent Amendments (30d): {len(overview['amendment_activity']['recent_amendments_30d'])}
• Most Common Type: {max(overview['amendment_activity']['amendment_types_12m'].items(), key=lambda x: x[1])[0] if overview['amendment_activity']['amendment_types_12m'] else 'None'}

⚙️  IMPLEMENTATION STATUS
──────────────────────────
• Overall Progress: {overview['implementation_status']['overall_progress']['completion_rate']}% 
• Completed: {overview['implementation_status']['overall_progress']['completed']}
• In Progress: {overview['implementation_status']['overall_progress']['in_progress']}
• Overdue: {len(overview['implementation_status']['overdue_implementations'])}

✅ COMPLIANCE SUMMARY
────────────────────────
• Legal Hierarchy Valid: {overview['compliance_summary']['legal_hierarchy']['valid_regulations']}
• Legal Violations: {overview['compliance_summary']['legal_hierarchy']['invalid_regulations']}
• International Compliant: {overview['compliance_summary']['international_alignment'].get('compliant', 0)}

🚨 SYSTEM ALERTS
──────────────────
"""
        
        if overview['alerts']:
            for alert in overview['alerts']:
                priority_icon = {'high': '🔴', 'medium': '🟡', 'low': '🟢'}.get(alert['priority'], '⚪')
                report += f"• {priority_icon} {alert['message']}\n"
        else:
            report += "• 🟢 No active alerts\n"
        
        report += f"""
════════════════════════════════════════════════════════════════
Report generated by KEMENKEU Legal Framework System
Dashboard operational at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
════════════════════════════════════════════════════════════════
"""
        
        return report
    
    def search_regulations(self, query: str, filters: Dict = None) -> List[Dict]:
        """Search regulations with advanced filtering"""
        filters = filters or {}
        
        try:
            with self.conn.cursor() as cur:
                # Build search query
                base_query = """
                    SELECT r.id, r.title, r.series, r.date_effective, r.status,
                           COUNT(c.id) as citation_count
                    FROM regulations r
                    LEFT JOIN citations c ON r.id = c.cited_regulation_id
                    WHERE r.title ILIKE %s
                """
                
                params = [f'%{query}%']
                
                # Apply filters
                if filters.get('type'):
                    base_query += " AND r.type = %s"
                    params.append(filters['type'])
                
                if filters.get('series'):
                    base_query += " AND r.series = %s"
                    params.append(filters['series'])
                
                if filters.get('status'):
                    base_query += " AND r.status = %s"
                    params.append(filters['status'])
                
                if filters.get('date_from'):
                    base_query += " AND r.date_effective >= %s"
                    params.append(filters['date_from'])
                
                if filters.get('date_to'):
                    base_query += " AND r.date_effective <= %s"
                    params.append(filters['date_to'])
                
                base_query += """
                    GROUP BY r.id, r.title, r.series, r.date_effective, r.status
                    ORDER BY citation_count DESC, r.date_effective DESC
                    LIMIT 50
                """
                
                cur.execute(base_query, params)
                
                results = []
                for row in cur.fetchall():
                    results.append({
                        'regulation_id': row[0],
                        'title': row[1],
                        'series': row[2],
                        'date_effective': row[3].isoformat() if row[3] else None,
                        'status': row[4],
                        'citation_count': row[5]
                    })
                
                return results
                
        except Exception as e:
            return [{'error': str(e)}]
    
    def get_regulation_details(self, regulation_id: str) -> Dict:
        """Get comprehensive details for a specific regulation"""
        details = {
            'regulation_info': {},
            'authority_chain': [],
            'citing_regulations': [],
            'amendment_history': [],
            'implementation_status': [],
            'international_alignment': []
        }
        
        try:
            with self.conn.cursor() as cur:
                # Basic regulation info
                cur.execute("""
                    SELECT id, type, number, year, series, title, subject_area, 
                           date_enacted, date_effective, status, issuing_authority, summary
                    FROM regulations WHERE id = %s
                """, (regulation_id,))
                
                reg_info = cur.fetchone()
                if reg_info:
                    details['regulation_info'] = {
                        'id': reg_info[0],
                        'type': reg_info[1],
                        'number': reg_info[2],
                        'year': reg_info[3],
                        'series': reg_info[4],
                        'title': reg_info[5],
                        'subject_area': reg_info[6],
                        'date_enacted': reg_info[7].isoformat() if reg_info[7] else None,
                        'date_effective': reg_info[8].isoformat() if reg_info[8] else None,
                        'status': reg_info[9],
                        'issuing_authority': reg_info[10],
                        'summary': reg_info[11]
                    }
                
                # Authority chain
                self.citation_analyzer.build_citation_network()
                details['authority_chain'] = self.citation_analyzer.find_authority_chain(regulation_id)
                
                # Citing regulations
                cur.execute("""
                    SELECT c.citing_regulation_id, r.title, c.citation_type
                    FROM citations c
                    JOIN regulations r ON c.citing_regulation_id = r.id
                    WHERE c.cited_regulation_id = %s
                    ORDER BY r.date_effective DESC
                """, (regulation_id,))
                
                details['citing_regulations'] = [
                    {'regulation_id': row[0], 'title': row[1], 'citation_type': row[2]}
                    for row in cur.fetchall()
                ]
                
                # Amendment history
                cur.execute("""
                    SELECT a.amending_regulation_id, r.title, a.amendment_type, 
                           a.amendment_date, a.description
                    FROM amendments a
                    JOIN regulations r ON a.amending_regulation_id = r.id
                    WHERE a.original_regulation_id = %s
                    ORDER BY a.amendment_date DESC
                """, (regulation_id,))
                
                details['amendment_history'] = [
                    {
                        'amending_regulation': row[0],
                        'title': row[1],
                        'type': row[2],
                        'date': row[3].isoformat() if row[3] else None,
                        'description': row[4]
                    }
                    for row in cur.fetchall()
                ]
                
                # Implementation status
                cur.execute("""
                    SELECT system_name, system_type, implementation_status, 
                           go_live_date, responsible_unit
                    FROM implementation_systems
                    WHERE regulation_id = %s
                """, (regulation_id,))
                
                details['implementation_status'] = [
                    {
                        'system': row[0],
                        'type': row[1],
                        'status': row[2],
                        'go_live_date': row[3].isoformat() if row[3] else None,
                        'responsible_unit': row[4]
                    }
                    for row in cur.fetchall()
                ]
                
                # International alignment
                cur.execute("""
                    SELECT agreement_name, agreement_type, alignment_status, 
                           compliance_requirements
                    FROM international_alignments
                    WHERE regulation_id = %s
                """, (regulation_id,))
                
                details['international_alignment'] = [
                    {
                        'agreement': row[0],
                        'type': row[1],
                        'status': row[2],
                        'requirements': row[3]
                    }
                    for row in cur.fetchall()
                ]
                
        except Exception as e:
            details['error'] = str(e)
        
        return details
    
    def export_dashboard_data(self, format='json') -> str:
        """Export complete dashboard data"""
        dashboard_data = {
            'export_timestamp': datetime.now().isoformat(),
            'system_overview': self.get_system_overview(),
            'regulation_matrix': json.loads(self.implementation_matrix.export_implementation_matrix()),
            'citation_network': json.loads(self.citation_analyzer.export_network_data('json')),
            'metadata': {
                'version': '1.0',
                'system': 'KEMENKEU Legal Framework',
                'components': ['citation_analyzer', 'amendment_tracker', 'implementation_matrix']
            }
        }
        
        if format == 'json':
            return json.dumps(dashboard_data, indent=2, ensure_ascii=False, default=str)
        else:
            return str(dashboard_data)

# COMMAND LINE INTERFACE
if __name__ == "__main__":
    import sys
    
    DB_CONFIG = {
        'host': 'localhost',
        'database': 'kemenkeu_legal',
        'user': 'postgres',
        'password': 'password'
    }
    
    dashboard = LegalFrameworkDashboard(DB_CONFIG)
    
    if len(sys.argv) < 2:
        print("KEMENKEU Legal Framework Dashboard")
        print("Usage: python legal_framework_dashboard.py <command>")
        print("\nCommands:")
        print("  overview    - System overview")
        print("  report      - Daily report")
        print("  search      - Search regulations")
        print("  details     - Get regulation details")
        print("  export      - Export dashboard data")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "overview":
        overview = dashboard.get_system_overview()
        print(json.dumps(overview, indent=2, ensure_ascii=False, default=str))
        
    elif command == "report":
        report = dashboard.generate_daily_report()
        print(report)
        
    elif command == "search" and len(sys.argv) > 2:
        query = sys.argv[2]
        results = dashboard.search_regulations(query)
        print(json.dumps(results, indent=2, ensure_ascii=False, default=str))
        
    elif command == "details" and len(sys.argv) > 2:
        regulation_id = sys.argv[2]
        details = dashboard.get_regulation_details(regulation_id)
        print(json.dumps(details, indent=2, ensure_ascii=False, default=str))
        
    elif command == "export":
        data = dashboard.export_dashboard_data()
        filename = f"kemenkeu_legal_framework_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(data)
        print(f"✅ Dashboard data exported to {filename}")
        
    else:
        print("Invalid command or missing parameters")
        print("Use: python legal_framework_dashboard.py overview|report|search|details|export")