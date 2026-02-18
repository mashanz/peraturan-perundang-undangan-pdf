#!/usr/bin/env python3
"""
KEMENKEU Legal Citation Network Analyzer - OPERATIONAL SYSTEM
Real-time legal cross-reference analysis and validation
"""

import psycopg2
import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime, timedelta
import re
import json
import requests
from typing import Dict, List, Tuple, Optional

class LegalCitationAnalyzer:
    """Operational legal citation network analysis system"""
    
    def __init__(self, db_config: Dict):
        self.db_config = db_config
        self.conn = None
        self.graph = nx.DiGraph()
        self.connect_db()
        
    def connect_db(self):
        """Connect to PostgreSQL database"""
        try:
            self.conn = psycopg2.connect(**self.db_config)
            print("✅ Database connection established")
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            
    def build_citation_network(self) -> nx.DiGraph:
        """Build complete citation network graph"""
        query = """
        SELECT c.citing_regulation_id, c.cited_regulation_id, c.citation_type, 
               c.citation_strength, r1.title as citing_title, r2.title as cited_title,
               r1.authority_level as citing_level, r2.authority_level as cited_level
        FROM citations c
        JOIN regulations r1 ON c.citing_regulation_id = r1.id
        JOIN regulations r2 ON c.cited_regulation_id = r2.id
        WHERE r1.status = 'active' AND r2.status = 'active'
        """
        
        with self.conn.cursor() as cur:
            cur.execute(query)
            citations = cur.fetchall()
            
        # Build network graph
        self.graph.clear()
        for citing, cited, ctype, strength, citing_title, cited_title, citing_level, cited_level in citations:
            self.graph.add_node(citing, title=citing_title, level=citing_level)
            self.graph.add_node(cited, title=cited_title, level=cited_level)
            self.graph.add_edge(citing, cited, 
                              citation_type=ctype, 
                              strength=strength,
                              weight=self._get_citation_weight(ctype, strength))
        
        print(f"✅ Citation network built: {len(self.graph.nodes)} regulations, {len(self.graph.edges)} citations")
        return self.graph
    
    def _get_citation_weight(self, citation_type: str, strength: str) -> float:
        """Calculate edge weight based on citation type and strength"""
        type_weights = {'mengingat': 1.0, 'implementing': 0.8, 'related': 0.5, 'amending': 0.9}
        strength_weights = {'mandatory': 1.0, 'supporting': 0.7, 'informational': 0.3}
        return type_weights.get(citation_type, 0.5) * strength_weights.get(strength, 0.5)
    
    def find_authority_chain(self, regulation_id: str) -> List[str]:
        """Find complete legal authority chain for a regulation"""
        if regulation_id not in self.graph:
            return []
            
        # Find all cited authorities (following mengingat edges)
        authority_chain = []
        current_nodes = [regulation_id]
        visited = set()
        
        while current_nodes:
            next_nodes = []
            for node in current_nodes:
                if node in visited:
                    continue
                    
                visited.add(node)
                authority_chain.append({
                    'regulation_id': node,
                    'title': self.graph.nodes[node].get('title', ''),
                    'level': self.graph.nodes[node].get('level', 0)
                })
                
                # Find cited authorities
                for successor in self.graph.successors(node):
                    edge_data = self.graph[node][successor]
                    if edge_data.get('citation_type') == 'mengingat':
                        next_nodes.append(successor)
            
            current_nodes = next_nodes
        
        # Sort by authority level (lower level = higher authority)
        authority_chain.sort(key=lambda x: x['level'])
        return authority_chain
    
    def validate_legal_hierarchy(self, regulation_id: str) -> Dict:
        """Validate legal hierarchy compliance"""
        validation_result = {
            'regulation_id': regulation_id,
            'is_valid': True,
            'violations': [],
            'warnings': [],
            'authority_chain': []
        }
        
        if regulation_id not in self.graph:
            validation_result['is_valid'] = False
            validation_result['violations'].append('Regulation not found in network')
            return validation_result
        
        reg_level = self.graph.nodes[regulation_id].get('level', 0)
        authority_chain = self.find_authority_chain(regulation_id)
        validation_result['authority_chain'] = authority_chain
        
        # Check if PMK cites primary law (UU)
        if reg_level == 4:  # PMK level
            has_primary_law = any(auth['level'] == 1 for auth in authority_chain)
            if not has_primary_law:
                validation_result['is_valid'] = False
                validation_result['violations'].append('PMK must cite primary law (UU)')
        
        # Check authority level consistency
        for auth in authority_chain:
            if auth['level'] >= reg_level and auth['regulation_id'] != regulation_id:
                validation_result['warnings'].append(
                    f"Citing same or lower level regulation: {auth['regulation_id']}"
                )
        
        return validation_result
    
    def find_regulation_impact(self, regulation_id: str) -> Dict:
        """Find all regulations impacted by changes to a regulation"""
        if regulation_id not in self.graph:
            return {'impacted_regulations': [], 'impact_levels': {}}
        
        # Use BFS to find all regulations that depend on this one
        impacted = []
        impact_levels = {}
        queue = [(regulation_id, 0)]
        visited = set()
        
        while queue:
            current_reg, level = queue.pop(0)
            if current_reg in visited:
                continue
                
            visited.add(current_reg)
            if level > 0:  # Don't include the original regulation
                impacted.append({
                    'regulation_id': current_reg,
                    'title': self.graph.nodes[current_reg].get('title', ''),
                    'impact_level': level
                })
                impact_levels[current_reg] = level
            
            # Find regulations that cite this one
            for predecessor in self.graph.predecessors(current_reg):
                if predecessor not in visited and level < 5:  # Limit depth
                    queue.append((predecessor, level + 1))
        
        # Sort by impact level
        impacted.sort(key=lambda x: x['impact_level'])
        
        return {
            'impacted_regulations': impacted,
            'impact_levels': impact_levels,
            'total_impact': len(impacted)
        }
    
    def detect_circular_references(self) -> List[List[str]]:
        """Detect circular citation patterns"""
        try:
            cycles = list(nx.simple_cycles(self.graph))
            return cycles
        except:
            return []
    
    def generate_compliance_report(self) -> Dict:
        """Generate comprehensive compliance report"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'total_regulations': len(self.graph.nodes),
            'total_citations': len(self.graph.edges),
            'validation_summary': {
                'valid_regulations': 0,
                'invalid_regulations': 0,
                'warning_regulations': 0
            },
            'violations': [],
            'circular_references': self.detect_circular_references()
        }
        
        # Validate all regulations
        for reg_id in self.graph.nodes:
            validation = self.validate_legal_hierarchy(reg_id)
            
            if validation['is_valid']:
                if validation['warnings']:
                    report['validation_summary']['warning_regulations'] += 1
                else:
                    report['validation_summary']['valid_regulations'] += 1
            else:
                report['validation_summary']['invalid_regulations'] += 1
                report['violations'].append({
                    'regulation_id': reg_id,
                    'violations': validation['violations']
                })
        
        return report
    
    def export_network_data(self, format='json') -> str:
        """Export network data for external analysis"""
        if format == 'json':
            data = {
                'nodes': [
                    {
                        'id': node,
                        'title': self.graph.nodes[node].get('title', ''),
                        'level': self.graph.nodes[node].get('level', 0)
                    }
                    for node in self.graph.nodes
                ],
                'edges': [
                    {
                        'source': edge[0],
                        'target': edge[1],
                        'citation_type': self.graph[edge[0]][edge[1]].get('citation_type', ''),
                        'strength': self.graph[edge[0]][edge[1]].get('strength', ''),
                        'weight': self.graph[edge[0]][edge[1]].get('weight', 0)
                    }
                    for edge in self.graph.edges
                ]
            }
            return json.dumps(data, indent=2, ensure_ascii=False)
        
        elif format == 'graphml':
            return '\n'.join(nx.generate_graphml(self.graph))
    
    def real_time_monitor(self, check_interval: int = 300):
        """Real-time monitoring of regulation changes"""
        print(f"🔄 Starting real-time monitoring (check every {check_interval}s)")
        
        last_check = datetime.now()
        while True:
            try:
                # Check for new regulations
                query = """
                SELECT COUNT(*) FROM regulations 
                WHERE created_at > %s AND status = 'active'
                """
                
                with self.conn.cursor() as cur:
                    cur.execute(query, (last_check,))
                    new_count = cur.fetchone()[0]
                
                if new_count > 0:
                    print(f"📢 {new_count} new regulations detected - rebuilding network")
                    self.build_citation_network()
                    
                    # Generate updated compliance report
                    report = self.generate_compliance_report()
                    print(f"📊 Network updated: {report['total_regulations']} regulations")
                    
                    # Check for violations
                    if report['validation_summary']['invalid_regulations'] > 0:
                        print(f"⚠️  {report['validation_summary']['invalid_regulations']} violations detected")
                
                last_check = datetime.now()
                
            except Exception as e:
                print(f"❌ Monitoring error: {e}")
            
            # Wait for next check
            import time
            time.sleep(check_interval)

# OPERATIONAL USAGE FUNCTIONS
def quick_analysis(regulation_id: str, db_config: Dict) -> Dict:
    """Quick analysis of a single regulation"""
    analyzer = LegalCitationAnalyzer(db_config)
    analyzer.build_citation_network()
    
    return {
        'authority_chain': analyzer.find_authority_chain(regulation_id),
        'validation': analyzer.validate_legal_hierarchy(regulation_id),
        'impact_analysis': analyzer.find_regulation_impact(regulation_id)
    }

def generate_daily_report(db_config: Dict) -> str:
    """Generate daily compliance report"""
    analyzer = LegalCitationAnalyzer(db_config)
    analyzer.build_citation_network()
    report = analyzer.generate_compliance_report()
    
    # Format report
    output = f"""
KEMENKEU LEGAL FRAMEWORK - DAILY COMPLIANCE REPORT
Generated: {report['timestamp']}

NETWORK STATISTICS:
- Total Regulations: {report['total_regulations']}
- Total Citations: {report['total_citations']}

VALIDATION SUMMARY:
- ✅ Valid: {report['validation_summary']['valid_regulations']}
- ⚠️  Warnings: {report['validation_summary']['warning_regulations']}
- ❌ Violations: {report['validation_summary']['invalid_regulations']}

"""
    
    if report['violations']:
        output += "VIOLATIONS FOUND:\n"
        for violation in report['violations'][:10]:  # Limit to first 10
            output += f"- {violation['regulation_id']}: {', '.join(violation['violations'])}\n"
    
    if report['circular_references']:
        output += f"\nCIRCULAR REFERENCES: {len(report['circular_references'])} detected\n"
    
    return output

# COMMAND LINE INTERFACE
if __name__ == "__main__":
    import sys
    
    # Database configuration
    DB_CONFIG = {
        'host': 'localhost',
        'database': 'kemenkeu_legal',
        'user': 'postgres',
        'password': 'password'
    }
    
    if len(sys.argv) < 2:
        print("Usage: python citation_network_analyzer.py <command> [regulation_id]")
        print("Commands: analyze, report, monitor, validate")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "analyze" and len(sys.argv) > 2:
        regulation_id = sys.argv[2]
        result = quick_analysis(regulation_id, DB_CONFIG)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
    elif command == "report":
        report = generate_daily_report(DB_CONFIG)
        print(report)
        
    elif command == "monitor":
        analyzer = LegalCitationAnalyzer(DB_CONFIG)
        analyzer.build_citation_network()
        analyzer.real_time_monitor()
        
    elif command == "validate" and len(sys.argv) > 2:
        regulation_id = sys.argv[2]
        analyzer = LegalCitationAnalyzer(DB_CONFIG)
        analyzer.build_citation_network()
        validation = analyzer.validate_legal_hierarchy(regulation_id)
        print(json.dumps(validation, indent=2, ensure_ascii=False))
        
    else:
        print("Invalid command or missing parameters")