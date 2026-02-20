import uuid
import os
from datetime import datetime
from database import get_connection
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from reportlab.lib.units import inch

class ExplainabilityEngine:
    
    @staticmethod
    def generate_explanation(case_id: str):
        conn = get_connection()
        
        # Get risk data
        risk = conn.execute('SELECT * FROM case_risk WHERE case_id = ?', (case_id,)).fetchone()
        if not risk:
            return "No risk analysis available"
        
        risk = dict(risk)
        
        # Get top contributors
        rule_count = conn.execute(
            'SELECT COUNT(*) as count FROM suspicious_events WHERE case_id = ?',
            (case_id,)
        ).fetchone()['count']
        
        anomaly_count = conn.execute(
            'SELECT COUNT(*) as count FROM anomaly_results WHERE case_id = ? AND is_anomaly = 1',
            (case_id,)
        ).fetchone()['count']
        
        conn.close()
        
        # Generate explanation
        explanation = f"Risk Level: {risk['risk_level'].upper()} (Score: {risk['total_score']:.1f}/100)\n\n"
        explanation += "Key Findings:\n"
        explanation += f"- {rule_count} rule violations detected\n"
        explanation += f"- {anomaly_count} anomalous events identified\n"
        explanation += f"- Rule contribution: {risk['rule_score_total']:.1f}\n"
        explanation += f"- Anomaly contribution: {risk['anomaly_score_total']:.1f}\n"
        explanation += f"- Network correlation: {risk['correlation_score']:.1f}\n\n"
        
        if risk['total_score'] >= 80:
            explanation += "CRITICAL: Immediate investigation required. Multiple high-severity indicators detected."
        elif risk['total_score'] >= 60:
            explanation += "HIGH RISK: Significant suspicious activity detected. Recommend detailed review."
        elif risk['total_score'] >= 40:
            explanation += "MEDIUM RISK: Some suspicious patterns identified. Monitor closely."
        else:
            explanation += "LOW RISK: Minimal suspicious activity detected."
        
        return explanation

class ReportEngine:
    
    @staticmethod
    def generate_report(case_id: str, title: str):
        conn = get_connection()
        
        # Get case data
        case = conn.execute('SELECT * FROM cases WHERE id = ?', (case_id,)).fetchone()
        risk = conn.execute('SELECT * FROM case_risk WHERE case_id = ?', (case_id,)).fetchone()
        suspicious = conn.execute('SELECT * FROM suspicious_events WHERE case_id = ? ORDER BY severity DESC LIMIT 10', (case_id,)).fetchall()
        anomalies = conn.execute('SELECT * FROM anomaly_results WHERE case_id = ? AND is_anomaly = 1 ORDER BY anomaly_score DESC LIMIT 10', (case_id,)).fetchall()
        
        if not case:
            conn.close()
            return None, "Case not found"
        
        case = dict(case)
        risk = dict(risk) if risk else None
        
        # Create reports directory
        os.makedirs('reports', exist_ok=True)
        
        # Generate unique filename with timestamp and case_id
        report_id = str(uuid.uuid4())
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        safe_case_name = ''.join(c if c.isalnum() else '_' for c in case['name'][:20])
        filename = f"reports/report_{safe_case_name}_{timestamp}_{report_id[:8]}.pdf"
        
        try:
            doc = SimpleDocTemplate(filename, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
            story = []
            styles = getSampleStyleSheet()
            
            # Custom styles
            title_style = ParagraphStyle('CustomTitle', parent=styles['Title'], fontSize=24, textColor=colors.HexColor('#1e40af'), spaceAfter=20)
            heading_style = ParagraphStyle('CustomHeading', parent=styles['Heading2'], fontSize=16, textColor=colors.HexColor('#1e40af'), spaceAfter=12, spaceBefore=12)
            
            # Title
            story.append(Paragraph(title, title_style))
            story.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
            story.append(Spacer(1, 20))
            
            # Case Info
            story.append(Paragraph("Case Information", heading_style))
            case_data = [
                ['Case Name:', case['name']],
                ['Description:', case['description']],
                ['Created:', case['created_at']],
                ['Status:', case['status']],
                ['Total Records:', str(case['records_count'])]
            ]
            case_table = Table(case_data, colWidths=[2*inch, 4.5*inch])
            case_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f3f4f6')),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
            ]))
            story.append(case_table)
            story.append(Spacer(1, 20))
            
            # Risk Assessment
            if risk:
                story.append(Paragraph("Risk Assessment", heading_style))
                risk_color = colors.red if risk['total_score'] >= 70 else colors.orange if risk['total_score'] >= 40 else colors.green
                story.append(Paragraph(f"<font color='{risk_color.hexval()}' size='14'><b>Overall Score: {risk['total_score']:.1f}/100 - {risk['risk_level'].upper()}</b></font>", styles['Normal']))
                story.append(Spacer(1, 10))
                
                risk_data = [
                    ['Metric', 'Score'],
                    ['Rule Violations', f"{risk['rule_score_total']:.1f}"],
                    ['Anomaly Detection', f"{risk['anomaly_score_total']:.1f}"],
                    ['Network Correlation', f"{risk['correlation_score']:.1f}"]
                ]
                risk_table = Table(risk_data, colWidths=[3*inch, 3.5*inch])
                risk_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e40af')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 10),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige)
                ]))
                story.append(risk_table)
                story.append(Spacer(1, 20))
            
            # Detailed Analysis
            explanation = ExplainabilityEngine.generate_explanation(case_id)
            story.append(Paragraph("Detailed Analysis", heading_style))
            for line in explanation.split('\n'):
                if line.strip():
                    story.append(Paragraph(line, styles['Normal']))
            story.append(Spacer(1, 20))
            
            # Top Violations
            if suspicious:
                story.append(Paragraph("Top Rule Violations", heading_style))
                viol_data = [['Rule Type', 'Severity', 'Description']]
                for s in suspicious:
                    viol_data.append([s['rule_type'], s['severity'], s['description'][:50] + '...'])
                viol_table = Table(viol_data, colWidths=[2*inch, 1.5*inch, 3*inch])
                viol_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e40af')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 9),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP')
                ]))
                story.append(viol_table)
                story.append(Spacer(1, 20))
            
            # Top Anomalies
            if anomalies:
                story.append(Paragraph("Top Anomalies Detected", heading_style))
                anom_data = [['Event ID', 'Anomaly Score', 'Timestamp']]
                for a in anomalies:
                    anom_data.append([a['event_id'][:20], f"{a['anomaly_score']:.3f}", a['created_at'][:19]])
                anom_table = Table(anom_data, colWidths=[2.5*inch, 2*inch, 2*inch])
                anom_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e40af')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 9),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
                ]))
                story.append(anom_table)
            
            # Build PDF
            doc.build(story)
            
            # Store report record
            conn.execute(
                'INSERT INTO reports VALUES (?, ?, ?, ?, ?, ?)',
                (report_id, case_id, title, explanation[:200], filename, datetime.now().isoformat())
            )
            conn.commit()
            
        except Exception as e:
            conn.close()
            import traceback
            traceback.print_exc()
            return None, str(e)
        
        conn.close()
        return report_id, filename
