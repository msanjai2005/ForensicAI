import os
import requests
from database import get_connection

class AIForensicAssistant:
    
    @staticmethod
    def build_case_context(case_id: str):
        """Build structured context from case data"""
        conn = get_connection()
        
        case = conn.execute('SELECT * FROM cases WHERE id = ?', (case_id,)).fetchone()
        risk = conn.execute('SELECT * FROM case_risk WHERE case_id = ?', (case_id,)).fetchone()
        rules = conn.execute(
            'SELECT rule_type, COUNT(*) as count, severity FROM suspicious_events WHERE case_id = ? GROUP BY rule_type',
            (case_id,)
        ).fetchall()
        anomalies = conn.execute(
            'SELECT COUNT(*) as count FROM anomaly_results WHERE case_id = ? AND is_anomaly = 1',
            (case_id,)
        ).fetchone()
        high_centrality = conn.execute(
            'SELECT COUNT(*) as count FROM graph_nodes WHERE case_id = ? AND centrality > 0.7',
            (case_id,)
        ).fetchone()
        
        conn.close()
        
        context = f"""Case Intelligence Summary:

Case ID: {case_id}
Total Events: {case['records_count'] if case else 0}
Status: {case['status'] if case else 'Unknown'}

Risk Assessment:
- Overall Risk Score: {risk['total_score'] if risk else 0:.1f}/100
- Risk Level: {risk['risk_level'].upper() if risk else 'UNKNOWN'}
- Rule Score: {risk['rule_score_total'] if risk else 0:.1f}
- Anomaly Score: {risk['anomaly_score_total'] if risk else 0:.1f}
- Network Correlation: {risk['correlation_score'] if risk else 0:.1f}

Rule Violations:
"""
        
        if rules:
            for rule in rules:
                context += f"- {rule['rule_type']}: {rule['count']} violations ({rule['severity']} severity)\n"
        else:
            context += "- No rule violations detected\n"
        
        context += f"""
Anomaly Detection:
- Anomalous Events: {anomalies['count'] if anomalies else 0}

Network Analysis:
- High Centrality Nodes: {high_centrality['count'] if high_centrality else 0}
"""
        
        return context
    
    @staticmethod
    def generate_intelligent_response(context: str, question: str):
        """Powerful intelligent analysis of actual case data"""
        import re
        question_lower = question.lower()
        
        # Extract metrics
        risk_score = float(re.search(r'Overall Risk Score: ([\d.]+)', context).group(1)) if re.search(r'Overall Risk Score: ([\d.]+)', context) else 0
        risk_level = re.search(r'Risk Level: (\w+)', context).group(1) if re.search(r'Risk Level: (\w+)', context) else 'UNKNOWN'
        total_events = int(re.search(r'Total Events: (\d+)', context).group(1)) if re.search(r'Total Events: (\d+)', context) else 0
        anomalies = int(re.search(r'Anomalous Events: (\d+)', context).group(1)) if re.search(r'Anomalous Events: (\d+)', context) else 0
        high_centrality = int(re.search(r'High Centrality Nodes: (\d+)', context).group(1)) if re.search(r'High Centrality Nodes: (\d+)', context) else 0
        
        rule_violations = {}
        for match in re.finditer(r'- ([^:]+): (\d+) violations \((\w+) severity\)', context):
            rule_violations[match.group(1)] = {'count': int(match.group(2)), 'severity': match.group(3)}
        
        total_violations = sum(v['count'] for v in rule_violations.values())
        
        # Main concerns
        if any(word in question_lower for word in ['concern', 'finding', 'issue', 'main', 'key', 'suspicious', 'security']):
            concerns = []
            if risk_score >= 70:
                concerns.append(f"🚨 CRITICAL RISK: Score {risk_score:.1f}/100 - Immediate investigation required")
            elif risk_score >= 50:
                concerns.append(f"⚠️ HIGH RISK: Score {risk_score:.1f}/100 - Detailed review needed")
            
            for rule, data in sorted(rule_violations.items(), key=lambda x: x[1]['count'], reverse=True):
                emoji = '🔴' if data['severity'] == 'critical' else '🟠' if data['severity'] == 'high' else '🟡'
                concerns.append(f"{emoji} {data['count']} {rule} violations ({data['severity'].upper()})")
            
            if anomalies > 100:
                concerns.append(f"📊 {anomalies} anomalous events - significant behavioral deviations")
            elif anomalies > 20:
                concerns.append(f"📊 {anomalies} anomalous events detected")
            
            if high_centrality > 5:
                concerns.append(f"🕸️ {high_centrality} high-influence entities in network")
            
            return "**🔍 KEY SECURITY CONCERNS:**\n\n" + "\n".join(concerns) if concerns else "✅ No critical concerns - low risk case"
        
        # Risk assessment
        elif any(word in question_lower for word in ['risk', 'score', 'assessment', 'level']):
            severity_emoji = '🔴' if risk_score >= 70 else '🟠' if risk_score >= 50 else '🟡' if risk_score >= 30 else '🟢'
            analysis = f"""**{severity_emoji} RISK ASSESSMENT:**

📊 Overall Score: {risk_score:.1f}/100
🎯 Risk Level: {risk_level.upper()}
📈 Total Events: {total_events}
⚠️ Total Violations: {total_violations}
📉 Anomalies: {anomalies}

**Violation Breakdown:**
"""
            for rule, data in sorted(rule_violations.items(), key=lambda x: x[1]['count'], reverse=True):
                emoji = '🔴' if data['severity'] == 'critical' else '🟠' if data['severity'] == 'high' else '🟡'
                analysis += f"{emoji} {rule}: {data['count']} ({data['severity']})\n"
            
            if risk_score >= 70:
                analysis += "\n⚠️ **CRITICAL RISK** - Immediate action required\n"
                analysis += "Recommend: Escalate to senior investigators"
            elif risk_score >= 50:
                analysis += "\n⚠️ **HIGH RISK** - Detailed investigation needed"
            else:
                analysis += "\n✅ **MODERATE/LOW RISK** - Continue monitoring"
            
            return analysis
        
        # Summary
        elif any(word in question_lower for word in ['summary', 'overview', 'explain', 'findings']):
            critical = sum(1 for v in rule_violations.values() if v['severity'] == 'critical')
            high = sum(1 for v in rule_violations.values() if v['severity'] == 'high')
            
            top_violations = sorted(rule_violations.items(), key=lambda x: x[1]['count'], reverse=True)[:3]
            
            return f"""**📋 INVESTIGATION SUMMARY:**

**Case Metrics:**
📁 Total Events: {total_events}
🎯 Risk Score: {risk_score:.1f}/100 ({risk_level.upper()})
⚠️ Violations: {total_violations} ({critical} critical, {high} high)
📊 Anomalies: {anomalies}
🕸️ Network Entities: {high_centrality} high-influence

**Top Violations:**
{chr(10).join([f'{i+1}. {r}: {d["count"]} events ({d["severity"]})' for i, (r, d) in enumerate(top_violations)]) if top_violations else '• None detected'}

**Assessment:**
{'🚨 REQUIRES IMMEDIATE INVESTIGATION' if risk_score >= 70 else '⚠️ REQUIRES DETAILED REVIEW' if risk_score >= 50 else '✅ LOW RISK - CONTINUE MONITORING'}

**Recommendation:**
{'Escalate to senior team and conduct deep forensic analysis' if risk_score >= 70 else 'Review flagged events and generate detailed report' if risk_score >= 50 else 'Monitor for pattern changes'}"""
        
        # Actions
        elif any(word in question_lower for word in ['action', 'recommend', 'next', 'should', 'priority', 'do']):
            actions = []
            priority = 1
            
            if 'High Value Transfer' in rule_violations:
                actions.append(f"{priority}. 💰 Investigate {rule_violations['High Value Transfer']['count']} high-value transfers - verify legitimacy")
                priority += 1
            
            if 'Midnight Activity' in rule_violations:
                actions.append(f"{priority}. 🌙 Review {rule_violations['Midnight Activity']['count']} midnight activities - check authorization")
                priority += 1
            
            if 'Transaction Burst' in rule_violations:
                actions.append(f"{priority}. ⚡ Analyze {rule_violations['Transaction Burst']['count']} transaction bursts - detect automation")
                priority += 1
            
            if 'Deleted Messages' in rule_violations:
                actions.append(f"{priority}. 🗑️ Examine {rule_violations['Deleted Messages']['count']} deleted messages - potential evidence tampering")
                priority += 1
            
            if anomalies > 20:
                actions.append(f"{priority}. 📊 Deep-dive into {anomalies} anomalous events - identify patterns")
                priority += 1
            
            if high_centrality > 3:
                actions.append(f"{priority}. 🕸️ Map network connections for {high_centrality} key entities")
                priority += 1
            
            actions.append(f"{priority}. 📄 Generate comprehensive investigation report")
            actions.append(f"{priority+1}. 👥 Brief investigation team on findings")
            
            return "**🎯 RECOMMENDED ACTIONS:**\n\n" + "\n".join(actions[:8])
        
        # Patterns
        elif any(word in question_lower for word in ['pattern', 'behavior', 'trend']):
            patterns = []
            if 'Midnight Activity' in rule_violations:
                patterns.append(f"🌙 Off-hours activity: {rule_violations['Midnight Activity']['count']} events between midnight-6am")
            if 'Transaction Burst' in rule_violations:
                patterns.append(f"⚡ Burst behavior: {rule_violations['Transaction Burst']['count']} rapid transaction sequences")
            if anomalies > 50:
                patterns.append(f"📊 Anomalous patterns: {anomalies} events deviate from baseline behavior")
            
            return "**🔍 DETECTED PATTERNS:**\n\n" + "\n".join(patterns) if patterns else "No significant patterns detected"
        
        # Users/Entities
        elif any(word in question_lower for word in ['user', 'entity', 'entities', 'who', 'actor']):
            return f"""**👥 ENTITY ANALYSIS:**

🕸️ High-Risk Entities: {high_centrality}
📊 Total Events: {total_events}
⚠️ Flagged Activities: {total_violations}

**Network Analysis:**
• {high_centrality} entities with high centrality scores
• These entities are central to communication/transaction networks
• Review Graph Intelligence page for detailed network map

**Recommendation:**
Focus investigation on high-centrality entities first"""
        
        # Anomalies
        elif any(word in question_lower for word in ['anomaly', 'anomalies', 'unusual', 'deviation']):
            return f"""**📊 ANOMALY DETECTION RESULTS:**

🔍 Anomalous Events: {anomalies}
📈 Total Events: {total_events}
📉 Anomaly Rate: {(anomalies/max(total_events,1)*100):.1f}%

**Analysis:**
{'🚨 HIGH anomaly rate - significant behavioral deviations' if anomalies > 100 else '⚠️ MODERATE anomaly rate - review flagged events' if anomalies > 20 else '✅ LOW anomaly rate - normal behavior'}

**What are anomalies?**
Events that deviate from baseline behavioral patterns using ML analysis

**Next Steps:**
1. Review Anomaly Detection page for details
2. Investigate high-score anomalies first
3. Correlate with rule violations"""
        
        # Midnight
        elif 'midnight' in question_lower:
            count = rule_violations.get('Midnight Activity', {}).get('count', 0)
            return f"""**🌙 MIDNIGHT ACTIVITY ANALYSIS:**

⚠️ Violations: {count}
⏰ Time Range: 00:00 - 06:00

**Why it matters:**
Off-hours activity often indicates:
• Unauthorized access
• Automated attacks
• Insider threats
• Data exfiltration

**Recommendation:**
{'🚨 CRITICAL - Investigate all midnight activities immediately' if count > 10 else '⚠️ Review midnight events for authorization' if count > 0 else '✅ No midnight violations detected'}"""
        
        # High value
        elif any(word in question_lower for word in ['high value', 'transfer', 'transaction', 'money']):
            count = rule_violations.get('High Value Transfer', {}).get('count', 0)
            return f"""**💰 HIGH-VALUE TRANSFER ANALYSIS:**

⚠️ Flagged Transfers: {count}
💵 Threshold: Transactions above normal baseline

**Risk Factors:**
• Unusual transaction amounts
• Potential money laundering
• Fraud indicators
• Unauthorized transfers

**Action Required:**
{'🚨 URGENT - Verify all high-value transfers' if count > 5 else '⚠️ Review flagged transactions' if count > 0 else '✅ No high-value violations'}"""
        
        # Network
        elif any(word in question_lower for word in ['network', 'connection', 'graph', 'relationship']):
            return f"""**🕸️ NETWORK INTELLIGENCE:**

📊 High-Centrality Entities: {high_centrality}
🔗 Total Events: {total_events}

**Network Analysis:**
• Identifies key players in communication/transaction networks
• High centrality = high influence/connectivity
• Reveals hidden relationships and patterns

**Key Findings:**
{'🚨 Multiple high-influence entities detected - potential coordination' if high_centrality > 5 else '⚠️ Some key entities identified' if high_centrality > 0 else '✅ No significant network patterns'}

**Next Steps:**
Review Graph Intelligence page for visual network map"""
        
        # Default
        return f"""**🤖 FORENSIC AI ASSISTANT**

**Quick Stats:**
📊 Risk: {risk_score:.1f}/100 ({risk_level.upper()})
⚠️ Violations: {total_violations}
📉 Anomalies: {anomalies}
📁 Events: {total_events}

**Ask me about:**
• "What are the main security concerns?" - Detailed threat analysis
• "What is the risk level?" - Comprehensive risk breakdown
• "Summarize all findings" - Complete investigation overview
• "What suspicious patterns exist?" - Behavioral analysis
• "Which users are high-risk?" - Entity identification
• "What actions should I take?" - Prioritized recommendations
• "Explain the anomalies" - ML detection results
• "Show midnight activity violations" - Off-hours analysis
• "What high-value transactions?" - Financial risk review
• "Analyze network connections" - Relationship mapping

💡 **Tip:** Ask specific questions for detailed forensic intelligence!"""
    
    @staticmethod
    def query_assistant(case_id: str, question: str):
        """Query AI assistant"""
        context = AIForensicAssistant.build_case_context(case_id)
        
        try:
            # Try Hugging Face
            hf_token = os.getenv('HUGGINGFACE_API_KEY')
            if hf_token:
                API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.1"
                headers = {"Authorization": f"Bearer {hf_token}"}
                prompt = f"<s>[INST] You are a forensic analyst.\n\n{context}\n\nQuestion: {question} [/INST]</s>"
                
                response = requests.post(API_URL, headers=headers, json={
                    "inputs": prompt,
                    "parameters": {"max_new_tokens": 300, "temperature": 0.3}
                }, timeout=30)
                
                if response.status_code == 200:
                    result = response.json()
                    if isinstance(result, list) and len(result) > 0:
                        text = result[0].get('generated_text', '')
                        if '[/INST]' in text:
                            text = text.split('[/INST]')[-1].strip()
                        if text:
                            return {'success': True, 'response': text, 'provider': 'huggingface'}
        except:
            pass
        
        # Use intelligent fallback
        return {
            'success': True,
            'response': AIForensicAssistant.generate_intelligent_response(context, question),
            'provider': 'intelligent_fallback'
        }
