# backend/api/utils.py
"""
Utility functions for data processing and PDF generation.
Uses Pandas for CSV parsing and ReportLab for PDF creation.
"""

import pandas as pd
import json
from io import StringIO, BytesIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch


def parse_csv_data(file_content):
    """
    Parse CSV file content using Pandas.
    
    Args:
        file_content: String or bytes of CSV data
    
    Returns:
        tuple: (data_list, dataframe) where data_list is list of dicts
    
    The function handles both string and bytes input,
    validates required columns, and returns cleaned data.
    """
    
    # Handle bytes input (from file upload)
    if isinstance(file_content, bytes):
        file_content = file_content.decode('utf-8')
    
    # Read CSV into DataFrame
    df = pd.read_csv(StringIO(file_content))
    
    # Define required columns
    required_columns = ['Equipment Name', 'Type', 'Flowrate', 'Pressure', 'Temperature']
    
    # Validate columns exist
    missing_cols = [col for col in required_columns if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}")
    
    # Clean data - remove rows with missing values
    df = df.dropna(subset=required_columns)
    
    # Convert numeric columns to proper types
    df['Flowrate'] = pd.to_numeric(df['Flowrate'], errors='coerce')
    df['Pressure'] = pd.to_numeric(df['Pressure'], errors='coerce')
    df['Temperature'] = pd.to_numeric(df['Temperature'], errors='coerce')
    
    # Convert to list of dictionaries for JSON storage
    data_list = df.to_dict('records')
    
    return data_list, df


def calculate_summary(df):
    """
    Calculate summary statistics from the DataFrame.
    
    Args:
        df: Pandas DataFrame with equipment data
    
    Returns:
        dict: Summary statistics including counts, averages, and distributions
    
    This provides all the analytics needed for the dashboard:
    - Total equipment count
    - Averages for numerical parameters
    - Min/Max values
    - Distribution by equipment type
    """
    
    summary = {
        # Total count of equipment
        'total_count': len(df),
        
        # Averages for each numerical parameter
        'averages': {
            'flowrate': round(df['Flowrate'].mean(), 2),
            'pressure': round(df['Pressure'].mean(), 2),
            'temperature': round(df['Temperature'].mean(), 2),
        },
        
        # Minimum values
        'minimums': {
            'flowrate': round(df['Flowrate'].min(), 2),
            'pressure': round(df['Pressure'].min(), 2),
            'temperature': round(df['Temperature'].min(), 2),
        },
        
        # Maximum values
        'maximums': {
            'flowrate': round(df['Flowrate'].max(), 2),
            'pressure': round(df['Pressure'].max(), 2),
            'temperature': round(df['Temperature'].max(), 2),
        },
        
        # Standard deviations
        'std_deviations': {
            'flowrate': round(df['Flowrate'].std(), 2),
            'pressure': round(df['Pressure'].std(), 2),
            'temperature': round(df['Temperature'].std(), 2),
        },
        
        # Equipment type distribution (count per type)
        'type_distribution': df['Type'].value_counts().to_dict(),
        
        # Equipment types list
        'equipment_types': df['Type'].unique().tolist(),
    }
    
    return summary


def generate_pdf_report(dataset):
    """
    Generate a PDF report for a dataset.
    
    Args:
        dataset: Dataset model instance
    
    Returns:
        BytesIO: PDF file as bytes buffer
    
    Creates a professional PDF report with:
    - Header with dataset info
    - Summary statistics table
    - Equipment type distribution
    - Full data table
    """
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.5*inch)
    elements = []
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=30,
        textColor=colors.HexColor('#2c3e50')
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=12,
        textColor=colors.HexColor('#34495e')
    )
    
    # Title
    elements.append(Paragraph("Chemical Equipment Parameter Report", title_style))
    elements.append(Paragraph(f"Dataset: {dataset.name}", styles['Normal']))
    elements.append(Paragraph(f"Generated: {dataset.uploaded_at.strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
    elements.append(Spacer(1, 20))
    
    # Get summary data
    summary = dataset.get_summary()
    
    # Summary Statistics Section
    elements.append(Paragraph("Summary Statistics", heading_style))
    
    summary_data = [
        ['Metric', 'Flowrate', 'Pressure', 'Temperature'],
        ['Average', 
         str(summary['averages']['flowrate']), 
         str(summary['averages']['pressure']), 
         str(summary['averages']['temperature'])],
        ['Minimum', 
         str(summary['minimums']['flowrate']), 
         str(summary['minimums']['pressure']), 
         str(summary['minimums']['temperature'])],
        ['Maximum', 
         str(summary['maximums']['flowrate']), 
         str(summary['maximums']['pressure']), 
         str(summary['maximums']['temperature'])],
        ['Std Dev', 
         str(summary['std_deviations']['flowrate']), 
         str(summary['std_deviations']['pressure']), 
         str(summary['std_deviations']['temperature'])],
    ]
    
    summary_table = Table(summary_data, colWidths=[1.5*inch, 1.2*inch, 1.2*inch, 1.2*inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#ecf0f1')),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#bdc3c7')),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('TOPPADDING', (0, 1), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
    ]))
    elements.append(summary_table)
    elements.append(Spacer(1, 20))
    
    # Type Distribution Section
    elements.append(Paragraph("Equipment Type Distribution", heading_style))
    
    type_data = [['Equipment Type', 'Count']]
    for eq_type, count in summary['type_distribution'].items():
        type_data.append([eq_type, str(count)])
    
    type_table = Table(type_data, colWidths=[2*inch, 1*inch])
    type_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#27ae60')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#e8f6f3')),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#bdc3c7')),
    ]))
    elements.append(type_table)
    elements.append(Spacer(1, 20))
    
    # Equipment Data Table
    elements.append(Paragraph("Equipment Data", heading_style))
    
    raw_data = dataset.get_raw_data()
    data_table_content = [['Equipment Name', 'Type', 'Flowrate', 'Pressure', 'Temperature']]
    
    for item in raw_data:
        data_table_content.append([
            item['Equipment Name'],
            item['Type'],
            str(item['Flowrate']),
            str(item['Pressure']),
            str(item['Temperature'])
        ])
    
    data_table = Table(data_table_content, colWidths=[1.5*inch, 1.2*inch, 0.9*inch, 0.9*inch, 1*inch])
    data_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#9b59b6')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f5eef8')),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#bdc3c7')),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
    ]))
    elements.append(data_table)
    
    # Build PDF
    doc.build(elements)
    buffer.seek(0)
    
    return buffer