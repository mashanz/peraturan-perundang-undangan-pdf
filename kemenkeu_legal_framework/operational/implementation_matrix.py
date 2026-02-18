#!/usr/bin/env python3
"""
KEMENKEU Implementation Requirement Matrix - OPERATIONAL SYSTEM
Real-time mapping of regulations to system implementation requirements
"""

import psycopg2
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import pandas as pd

class ImplementationMatrix:
    """Operational system for mapping regulations to implementation requirements"""
    
    def __init__(self, db_config: Dict):
        self.db_config = db_config
        self.conn = None
        self.connect_db()
        
        # KEMENKEU Core Systems
        self.core_systems = {
            'SPAN': {
                'name': 'Sistem Penerimaan Negara',
                'type': 'core',
                'responsible_unit': 'DJP',
                'categories': ['tax_administration', 'customs', 'non_tax_revenue'],
                'api_endpoint': 'https://span.kemenkeu.go.id/api',
                'typical_implementation_days': 45
            },
            'SAKTI': {
                'name': 'Sistem Aplikasi Keuangan Tingkat Instansi', 
                'type': 'core',
                'responsible_unit': 'Setjen',
                'categories': ['budget_management', 'expenditure', 'accounting'],
                'api_endpoint': 'https://sakti.kemenkeu.go.id/api',
                'typical_implementation_days': 60
            },
            'SIAP': {
                'name': 'Sistem Informasi dan Administrasi Perpajakan',
                'type': 'supporting',
                'responsible_unit': 'DJP',
                'categories': ['taxpayer_services', 'compliance_monitoring'],
                'api_endpoint': 'https://siap.pajak.go.id/api',
                'typical_implementation_days': 30
            },
            'OMSPAN': {
                'name': 'Online Monitoring SPAN',
                'type': 'monitoring',
                'responsible_unit': 'DJP',
                'categories': ['performance_monitoring', 'analytics'],
                'api_endpoint': 'https://omspan.kemenkeu.go.id/api',
                'typical_implementation_days': 15
            },
            'CEISA': {
                'name': 'Customs Electronic Import System',
                'type': 'core',
                'responsible_unit': 'DJBC',
                'categories': ['customs', 'trade_facilitation'],
                'api_endpoint': 'https://ceisa.customs.go.id/api',
                'typical_implementation_days': 40
            }
        }
        
        # PMK Series to System Mapping
        self.series_mapping = {
            'PMK.01': ['SAKTI', 'SPAN'],  # Budget and Treasury
            'PMK.02': ['SAKTI'],          # State Financial Management
            'PMK.03': ['SPAN', 'SIAP', 'OMSPAN'],  # Tax Administration
            'PMK.04': ['SPAN', 'CEISA'],  # Customs and Excise
            'PMK.05': ['SAKTI'],          # Government Accounting
            'PMK.06': ['SPAN', 'SIAP'],   # Tax Policy
        }
    
    def connect_db(self):
        """Connect to PostgreSQL database"""
        try:
            self.conn = psycopg2.connect(**self.db_config)
            print("✅ Implementation matrix database connected")
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
    
    def analyze_regulation_requirements(self, regulation_id: str) -> Dict:
        """Analyze implementation requirements for a regulation"""
        try:
            with self.conn.cursor() as cur:
                # Get regulation details
                cur.execute("""
                    SELECT id, type, series, title, subject_area, date_enacted, date_effective
                    FROM regulations WHERE id = %s
                """, (regulation_id,))
                
                reg_data = cur.fetchone()
                if not reg_data:
                    return {'error': 'Regulation not found'}
                
                reg_id, reg_type, series, title, subject_area, date_enacted, date_effective = reg_data
                
                # Determine applicable systems
                applicable_systems = self._determine_applicable_systems(series, subject_area, title)
                
                # Get existing implementation records
                cur.execute("""
                    SELECT system_name, system_type, integration_level, implementation_status, 
                           go_live_date, responsible_unit
                    FROM implementation_systems WHERE regulation_id = %s
                """, (regulation_id,))
                
                existing_implementations = cur.fetchall()
                
                # Generate implementation requirements
                requirements = self._generate_implementation_requirements(
                    reg_data, applicable_systems, existing_implementations
                )
                
                return requirements
                
        except Exception as e:
            print(f"❌ Error analyzing requirements: {e}")
            return {'error': str(e)}
    
    def _determine_applicable_systems(self, series: str, subject_area: str, title: str) -> List[str]:
        """Determine which systems are applicable for a regulation"""
        applicable = []
        
        # Primary mapping by PMK series
        if series in self.series_mapping:
            applicable.extend(self.series_mapping[series])
        
        # Secondary mapping by subject area and title keywords
        title_lower = title.lower()
        subject_lower = (subject_area or '').lower()
        
        keywords_mapping = {
            'SPAN': ['pajak', 'tax', 'penerimaan negara', 'bea cukai', 'customs'],
            'SAKTI': ['anggaran', 'budget', 'keuangan negara', 'belanja', 'akuntansi'],
            'SIAP': ['wajib pajak', 'taxpayer', 'administrasi pajak'],
            'CEISA': ['pabean', 'customs', 'impor', 'ekspor', 'import', 'export'],
            'OMSPAN': ['monitoring', 'pelaporan', 'reporting', 'analytics']
        }
        
        for system, keywords in keywords_mapping.items():
            if any(keyword in title_lower or keyword in subject_lower for keyword in keywords):
                if system not in applicable:
                    applicable.append(system)
        
        return applicable
    
    def _generate_implementation_requirements(self, reg_data, applicable_systems: List[str], existing: List) -> Dict:
        """Generate detailed implementation requirements"""
        reg_id, reg_type, series, title, subject_area, date_enacted, date_effective = reg_data
        
        requirements = {
            'regulation_id': reg_id,
            'regulation_title': title,
            'analysis_date': datetime.now().isoformat(),
            'applicable_systems': [],
            'implementation_timeline': {},
            'resource_requirements': {},
            'dependencies': [],
            'risk_assessment': {}
        }
        
        existing_dict = {row[0]: row for row in existing}
        
        for system_name in applicable_systems:
            if system_name not in self.core_systems:
                continue
                
            system_info = self.core_systems[system_name]
            existing_impl = existing_dict.get(system_name)
            
            system_req = {
                'system_name': system_name,
                'system_type': system_info['type'],
                'responsible_unit': system_info['responsible_unit'],
                'integration_level': self._determine_integration_level(reg_data, system_name),
                'current_status': existing_impl[3] if existing_impl else 'not_planned',
                'required_changes': self._identify_required_changes(reg_data, system_name),
                'estimated_effort_days': self._estimate_implementation_effort(reg_data, system_name),
                'technical_requirements': self._generate_technical_requirements(reg_data, system_name),
                'testing_requirements': self._generate_testing_requirements(reg_data, system_name)
            }
            
            requirements['applicable_systems'].append(system_req)
        
        # Generate timeline
        requirements['implementation_timeline'] = self._generate_implementation_timeline(
            requirements['applicable_systems'], date_effective
        )
        
        # Resource requirements
        requirements['resource_requirements'] = self._calculate_resource_requirements(
            requirements['applicable_systems']
        )
        
        # Dependencies
        requirements['dependencies'] = self._identify_dependencies(reg_data, applicable_systems)
        
        # Risk assessment
        requirements['risk_assessment'] = self._assess_implementation_risks(
            reg_data, requirements['applicable_systems']
        )
        
        return requirements
    
    def _determine_integration_level(self, reg_data, system_name: str) -> str:
        """Determine integration level required"""
        reg_id, reg_type, series, title, subject_area, date_enacted, date_effective = reg_data
        
        # Critical systems for core PMK series
        if series in ['PMK.01', 'PMK.03'] and system_name in ['SPAN', 'SAKTI']:
            return 'required'
        
        # Supporting integrations
        if system_name in ['SIAP', 'OMSPAN']:
            return 'recommended'
        
        return 'optional'
    
    def _identify_required_changes(self, reg_data, system_name: str) -> List[str]:
        """Identify specific changes required in system"""
        reg_id, reg_type, series, title, subject_area, date_enacted, date_effective = reg_data
        
        changes = []
        title_lower = title.lower()
        
        # Common change patterns
        if 'elektronik' in title_lower or 'electronic' in title_lower:
            changes.extend(['UI updates for electronic processes', 'Database schema updates', 'API integration'])
        
        if 'tarif' in title_lower or 'rate' in title_lower:
            changes.extend(['Rate calculation engine updates', 'Validation rule updates'])
        
        if 'prosedur' in title_lower or 'procedure' in title_lower:
            changes.extend(['Workflow engine modifications', 'Business rule updates'])
        
        if 'pelaporan' in title_lower or 'reporting' in title_lower:
            changes.extend(['Report template updates', 'Data aggregation logic'])
        
        # System-specific changes
        system_specific_changes = {
            'SPAN': ['Transaction processing updates', 'Revenue calculation modifications'],
            'SAKTI': ['Budget allocation logic', 'Expenditure control updates'],
            'SIAP': ['Taxpayer interface updates', 'Compliance checking logic'],
            'CEISA': ['Trade documentation updates', 'Customs clearance procedures'],
            'OMSPAN': ['Monitoring dashboard updates', 'Performance metric calculations']
        }
        
        if system_name in system_specific_changes:
            changes.extend(system_specific_changes[system_name])
        
        return list(set(changes))  # Remove duplicates
    
    def _estimate_implementation_effort(self, reg_data, system_name: str) -> int:
        """Estimate implementation effort in person-days"""
        reg_id, reg_type, series, title, subject_area, date_enacted, date_effective = reg_data
        
        base_effort = self.core_systems[system_name]['typical_implementation_days']
        
        # Complexity multipliers
        multiplier = 1.0
        
        title_lower = title.lower()
        if 'elektronik' in title_lower:
            multiplier *= 1.5  # Electronic systems are more complex
        
        if 'perubahan' in title_lower or 'amend' in title_lower:
            multiplier *= 0.7  # Amendments typically require less effort
        
        if 'sistem' in title_lower or 'system' in title_lower:
            multiplier *= 1.3  # System-wide changes
        
        # Series-based adjustments
        series_multipliers = {
            'PMK.01': 1.2,  # Budget regulations are complex
            'PMK.03': 1.0,  # Tax regulations are standard
            'PMK.04': 1.1,  # Customs can be complex
            'PMK.05': 0.9   # Accounting standards are usually straightforward
        }
        
        if series in series_multipliers:
            multiplier *= series_multipliers[series]
        
        return int(base_effort * multiplier)
    
    def _generate_technical_requirements(self, reg_data, system_name: str) -> Dict:
        """Generate technical implementation requirements"""
        reg_id, reg_type, series, title, subject_area, date_enacted, date_effective = reg_data
        
        requirements = {
            'database_changes': [],
            'api_modifications': [],
            'ui_updates': [],
            'integration_points': [],
            'security_requirements': [],
            'performance_requirements': {}
        }
        
        title_lower = title.lower()
        
        # Database changes
        if 'tarif' in title_lower or 'rate' in title_lower:
            requirements['database_changes'].append('Update rate tables and calculation logic')
        
        if 'elektronik' in title_lower:
            requirements['database_changes'].extend([
                'Add electronic document tracking tables',
                'Implement digital signature validation'
            ])
        
        # API modifications
        if system_name in ['SPAN', 'SAKTI']:
            requirements['api_modifications'].extend([
                'Update calculation endpoints',
                'Add new validation endpoints',
                'Implement compliance checking APIs'
            ])
        
        # UI updates
        requirements['ui_updates'].extend([
            'Update forms and validation messages',
            'Add new workflow screens',
            'Update reporting interfaces'
        ])
        
        # Performance requirements
        requirements['performance_requirements'] = {
            'response_time_ms': 2000,
            'concurrent_users': 1000,
            'availability_percent': 99.9,
            'throughput_tps': 100
        }
        
        # Security requirements
        requirements['security_requirements'] = [
            'Role-based access control updates',
            'Audit trail enhancements',
            'Data encryption compliance'
        ]
        
        return requirements
    
    def _generate_testing_requirements(self, reg_data, system_name: str) -> Dict:
        """Generate testing requirements"""
        return {
            'unit_testing': {
                'coverage_target': 85,
                'focus_areas': ['calculation logic', 'validation rules', 'workflow engines']
            },
            'integration_testing': {
                'test_scenarios': [
                    'End-to-end transaction processing',
                    'Cross-system data synchronization',
                    'Error handling and recovery'
                ],
                'external_systems': ['other KEMENKEU systems', 'external APIs']
            },
            'user_acceptance_testing': {
                'user_groups': ['internal staff', 'external stakeholders'],
                'test_duration_days': 14,
                'success_criteria': 'User satisfaction > 85%'
            },
            'performance_testing': {
                'load_testing': 'Simulate peak usage scenarios',
                'stress_testing': '150% of expected load',
                'endurance_testing': '24-hour continuous operation'
            }
        }
    
    def _generate_implementation_timeline(self, systems: List[Dict], effective_date) -> Dict:
        """Generate implementation timeline"""
        timeline = {
            'phases': [],
            'critical_path': [],
            'milestones': {}
        }
        
        # Sort systems by complexity (core systems first)
        systems_sorted = sorted(systems, key=lambda x: (
            0 if x['system_type'] == 'core' else 1,
            x['estimated_effort_days']
        ), reverse=True)
        
        current_date = datetime.now().date()
        target_date = effective_date
        
        if isinstance(target_date, str):
            target_date = datetime.strptime(target_date, '%Y-%m-%d').date()
        
        available_days = (target_date - current_date).days
        
        phases = ['analysis', 'development', 'testing', 'deployment']
        phase_percentages = [0.15, 0.60, 0.20, 0.05]
        
        for i, phase in enumerate(phases):
            phase_duration = int(available_days * phase_percentages[i])
            timeline['phases'].append({
                'phase': phase,
                'duration_days': phase_duration,
                'systems': [s['system_name'] for s in systems_sorted if s['integration_level'] == 'required']
            })
        
        return timeline
    
    def _calculate_resource_requirements(self, systems: List[Dict]) -> Dict:
        """Calculate resource requirements"""
        total_effort = sum(s['estimated_effort_days'] for s in systems)
        
        return {
            'total_effort_days': total_effort,
            'team_composition': {
                'business_analysts': max(1, total_effort // 60),
                'developers': max(2, total_effort // 30),
                'testers': max(1, total_effort // 45),
                'project_managers': 1
            },
            'budget_estimate_idr': total_effort * 2500000,  # 2.5M per person-day
            'infrastructure_requirements': {
                'development_environments': len(systems),
                'testing_environments': len(systems),
                'additional_hardware': total_effort > 100
            }
        }
    
    def _identify_dependencies(self, reg_data, systems: List[str]) -> List[Dict]:
        """Identify implementation dependencies"""
        dependencies = []
        
        # Inter-system dependencies
        if 'SPAN' in systems and 'SAKTI' in systems:
            dependencies.append({
                'type': 'system_integration',
                'dependency': 'SPAN-SAKTI data synchronization',
                'impact': 'Both systems must be updated simultaneously'
            })
        
        if 'SIAP' in systems and 'SPAN' in systems:
            dependencies.append({
                'type': 'system_integration', 
                'dependency': 'SIAP-SPAN taxpayer data consistency',
                'impact': 'Taxpayer updates must propagate between systems'
            })
        
        # External dependencies
        dependencies.extend([
            {
                'type': 'regulatory',
                'dependency': 'Legal interpretation clarifications',
                'impact': 'May affect technical requirements'
            },
            {
                'type': 'infrastructure',
                'dependency': 'Network connectivity and security',
                'impact': 'Required for system integration'
            }
        ])
        
        return dependencies
    
    def _assess_implementation_risks(self, reg_data, systems: List[Dict]) -> Dict:
        """Assess implementation risks"""
        risks = {
            'high_risks': [],
            'medium_risks': [],
            'low_risks': [],
            'mitigation_strategies': {}
        }
        
        # Timeline risks
        total_effort = sum(s['estimated_effort_days'] for s in systems)
        if total_effort > 120:
            risks['high_risks'].append({
                'risk': 'Implementation timeline may be insufficient',
                'probability': 'high',
                'impact': 'Delayed go-live'
            })
            risks['mitigation_strategies']['timeline'] = 'Parallel development tracks, additional resources'
        
        # Complexity risks
        core_systems_count = len([s for s in systems if s['system_type'] == 'core'])
        if core_systems_count > 2:
            risks['medium_risks'].append({
                'risk': 'Multi-system integration complexity',
                'probability': 'medium',
                'impact': 'Integration issues, testing delays'
            })
            risks['mitigation_strategies']['complexity'] = 'Comprehensive integration testing, staged rollout'
        
        # Resource risks
        risks['medium_risks'].append({
            'risk': 'Resource availability constraints',
            'probability': 'medium', 
            'impact': 'Development delays'
        })
        risks['mitigation_strategies']['resources'] = 'Early resource allocation, external contractor backup'
        
        return risks
    
    def generate_implementation_plan(self, regulation_id: str) -> Dict:
        """Generate complete implementation plan"""
        requirements = self.analyze_regulation_requirements(regulation_id)
        
        if 'error' in requirements:
            return requirements
        
        plan = {
            'regulation_id': regulation_id,
            'plan_generated': datetime.now().isoformat(),
            'requirements_analysis': requirements,
            'action_items': self._generate_action_items(requirements),
            'monitoring_plan': self._generate_monitoring_plan(requirements),
            'success_metrics': self._define_success_metrics(requirements)
        }
        
        return plan
    
    def _generate_action_items(self, requirements: Dict) -> List[Dict]:
        """Generate specific action items"""
        actions = []
        
        for system in requirements['applicable_systems']:
            if system['integration_level'] == 'required':
                actions.append({
                    'action': f"Implement {system['system_name']} changes",
                    'responsible_unit': system['responsible_unit'],
                    'priority': 'high',
                    'estimated_effort': system['estimated_effort_days'],
                    'dependencies': [dep['dependency'] for dep in requirements['dependencies']],
                    'due_date': (datetime.now() + timedelta(days=system['estimated_effort_days'])).date().isoformat()
                })
        
        # Add coordination actions
        actions.append({
            'action': 'Coordinate inter-system integration testing',
            'responsible_unit': 'Setjen',
            'priority': 'high',
            'estimated_effort': 10,
            'due_date': (datetime.now() + timedelta(days=45)).date().isoformat()
        })
        
        return actions
    
    def _generate_monitoring_plan(self, requirements: Dict) -> Dict:
        """Generate monitoring and tracking plan"""
        return {
            'progress_tracking': {
                'frequency': 'weekly',
                'metrics': ['tasks_completed', 'effort_consumed', 'timeline_adherence'],
                'reporting_to': ['project_sponsors', 'system_owners']
            },
            'quality_gates': {
                'design_review': 'Week 2',
                'code_review': 'Week 6', 
                'integration_testing': 'Week 8',
                'user_acceptance': 'Week 10'
            },
            'escalation_triggers': {
                'schedule_delay': '> 1 week behind plan',
                'budget_overrun': '> 10% over budget',
                'quality_issues': '> 5 critical defects'
            }
        }
    
    def _define_success_metrics(self, requirements: Dict) -> Dict:
        """Define success metrics"""
        return {
            'delivery_metrics': {
                'on_time_delivery': 'All systems go-live by effective date',
                'quality_target': '< 2% post-implementation defects',
                'budget_adherence': 'Within 5% of estimated budget'
            },
            'operational_metrics': {
                'system_availability': '> 99.5% uptime',
                'user_satisfaction': '> 85% satisfaction score',
                'performance_targets': 'Response time < 2 seconds'
            },
            'compliance_metrics': {
                'regulation_coverage': '100% of requirements implemented',
                'audit_readiness': 'Pass regulatory compliance audit',
                'documentation_completeness': 'All technical docs updated'
            }
        }
    
    def export_implementation_matrix(self) -> str:
        """Export complete implementation matrix"""
        try:
            with self.conn.cursor() as cur:
                # Get all active PMK regulations
                cur.execute("""
                    SELECT id, series, title, date_effective, status
                    FROM regulations 
                    WHERE type = 'PMK' AND status = 'active'
                    ORDER BY date_effective DESC
                """)
                
                regulations = cur.fetchall()
                
                matrix_data = []
                for reg_id, series, title, date_effective, status in regulations:
                    req_analysis = self.analyze_regulation_requirements(reg_id)
                    
                    if 'error' not in req_analysis:
                        matrix_data.append({
                            'regulation_id': reg_id,
                            'series': series,
                            'title': title[:100],  # Truncate for readability
                            'effective_date': date_effective.isoformat() if date_effective else '',
                            'applicable_systems': [s['system_name'] for s in req_analysis['applicable_systems']],
                            'total_effort_days': req_analysis['resource_requirements']['total_effort_days'],
                            'implementation_status': self._get_overall_implementation_status(reg_id)
                        })
                
                return json.dumps(matrix_data, indent=2, ensure_ascii=False, default=str)
                
        except Exception as e:
            return f"Error exporting matrix: {e}"
    
    def _get_overall_implementation_status(self, regulation_id: str) -> str:
        """Get overall implementation status for a regulation"""
        try:
            with self.conn.cursor() as cur:
                cur.execute("""
                    SELECT implementation_status, COUNT(*) as count
                    FROM implementation_systems 
                    WHERE regulation_id = %s
                    GROUP BY implementation_status
                """, (regulation_id,))
                
                statuses = dict(cur.fetchall())
                
                if not statuses:
                    return 'not_planned'
                
                if statuses.get('completed', 0) == sum(statuses.values()):
                    return 'completed'
                elif statuses.get('in_progress', 0) > 0:
                    return 'in_progress'
                else:
                    return 'planned'
                    
        except Exception as e:
            return 'unknown'

# COMMAND LINE INTERFACE
if __name__ == "__main__":
    import sys
    
    DB_CONFIG = {
        'host': 'localhost',
        'database': 'kemenkeu_legal',
        'user': 'postgres',
        'password': 'password'
    }
    
    matrix = ImplementationMatrix(DB_CONFIG)
    
    if len(sys.argv) < 2:
        print("Usage: python implementation_matrix.py <command> [regulation_id]")
        print("Commands: analyze, plan, export, matrix")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "analyze" and len(sys.argv) > 2:
        regulation_id = sys.argv[2]
        result = matrix.analyze_regulation_requirements(regulation_id)
        print(json.dumps(result, indent=2, ensure_ascii=False, default=str))
        
    elif command == "plan" and len(sys.argv) > 2:
        regulation_id = sys.argv[2]
        plan = matrix.generate_implementation_plan(regulation_id)
        print(json.dumps(plan, indent=2, ensure_ascii=False, default=str))
        
    elif command == "export":
        matrix_export = matrix.export_implementation_matrix()
        with open(f'implementation_matrix_{datetime.now().strftime("%Y%m%d")}.json', 'w') as f:
            f.write(matrix_export)
        print("✅ Implementation matrix exported")
        
    elif command == "matrix":
        matrix_export = matrix.export_implementation_matrix()
        print(matrix_export)
        
    else:
        print("Invalid command or missing parameters")