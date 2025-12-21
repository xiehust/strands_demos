---
name: work-summary
description: Professional work summary report creation with support for various formats and time periods. Use when users need to create work summaries, progress reports, performance reviews, project status reports, or periodic work documentation. Supports daily, weekly, monthly, quarterly, and annual summaries in multiple formats (DOCX, PPTX, Markdown, PDF).
---

# Work Summary Report Generator

## Overview

Generate professional work summary reports for various time periods and purposes. This skill helps create structured, comprehensive summaries of work accomplishments, progress, and outcomes.

## Report Types

### 1. Daily/Weekly Summary
Quick updates on recent work activities and immediate progress.

**Typical contents:**
- Tasks completed
- Current focus areas
- Blockers or challenges
- Next steps
- Key metrics (if applicable)

### 2. Monthly Summary
Comprehensive overview of monthly achievements and progress toward goals.

**Typical contents:**
- Major accomplishments
- Project milestones reached
- KPIs and metrics
- Challenges faced and solutions
- Upcoming priorities
- Team collaboration highlights

### 3. Quarterly Summary
Strategic review of quarterly performance and goal achievement.

**Typical contents:**
- Quarter highlights and achievements
- Goal completion status
- Key performance indicators
- Strategic initiatives progress
- Lessons learned
- Next quarter objectives

### 4. Annual Summary
Comprehensive year-end review of achievements and growth.

**Typical contents:**
- Year overview and major achievements
- Annual goals assessment
- Skills developed
- Impact and contributions
- Career growth
- Future objectives

### 5. Project Status Report
Focused update on specific project progress.

**Typical contents:**
- Project overview
- Current status and phase
- Deliverables completed
- Timeline and milestones
- Budget status (if applicable)
- Risks and mitigation
- Next steps

## Workflow

### Step 1: Gather Information

Ask the user to provide:
1. **Report type and time period** (daily, weekly, monthly, quarterly, annual, project-specific)
2. **Output format** (DOCX, PPTX, Markdown, PDF)
3. **Key information**:
   - Accomplishments and completed tasks
   - Current projects and initiatives
   - Metrics and KPIs (if applicable)
   - Challenges and blockers
   - Future goals and plans
   - Team or stakeholder information

**Approach**: Use clarifying questions to gather complete information. See [references/questions.md](references/questions.md) for question templates.

### Step 2: Select Template

Choose appropriate template based on report type and format:
- **DOCX reports**: Use docx-js for professional document creation
- **PPTX reports**: Use html2pptx for slide-based summaries
- **Markdown reports**: Use structured markdown with clear sections
- **PDF reports**: Create DOCX or Markdown first, then convert

Template structures are available in [references/templates.md](references/templates.md).

### Step 3: Structure Content

Organize information using appropriate structure:

**Professional format guidelines**:
- Clear hierarchy with headings and subheadings
- Bullet points for lists and accomplishments
- Tables for metrics and KPIs
- Concise, action-oriented language
- Quantifiable achievements when possible
- Professional tone and formatting

See [references/writing-guide.md](references/writing-guide.md) for detailed content structuring guidance.

### Step 4: Generate Report

Create the report using the selected format:

**For DOCX**:
1. Read the docx skill's documentation for document creation
2. Use Document, Paragraph, TextRun components
3. Apply professional formatting (headings, bullets, tables)
4. Export as .docx

**For PPTX**:
1. Read the pptx skill's documentation for presentation creation
2. Design appropriate slide layouts
3. Use professional color schemes and typography
4. Create clear visual hierarchy

**For Markdown**:
1. Use structured headings (H1, H2, H3)
2. Format lists with bullets or numbers
3. Include tables for data
4. Apply consistent formatting

### Step 5: Review and Refine

Verify report quality:
- All requested information included
- Professional formatting and structure
- Clear and concise language
- Accurate data and metrics
- Appropriate length for report type
- No spelling or grammar errors

## Format-Specific Guidelines

### DOCX Reports
- Use professional fonts (Calibri, Arial, Times New Roman)
- Apply consistent heading styles
- Include headers/footers with dates and page numbers
- Use tables for structured data
- Add visual elements sparingly (emphasis on content)

### PPTX Reports
- Limit text per slide (6-8 bullet points max)
- Use visual hierarchy (size, color, placement)
- Include data visualizations for metrics
- Consistent design across slides
- Clear slide titles

### Markdown Reports
- Use consistent heading levels
- Format code blocks for technical content
- Use tables for comparative data
- Include links to relevant resources
- Maintain readability in plain text

## Best Practices

### Writing Guidelines
1. **Be specific**: Use concrete examples and data
2. **Be concise**: Focus on key accomplishments and insights
3. **Be professional**: Maintain appropriate tone and language
4. **Be honest**: Acknowledge challenges and areas for improvement
5. **Be forward-looking**: Include plans and next steps

### Content Guidelines
1. **Quantify achievements**: Use numbers, percentages, metrics
2. **Highlight impact**: Show how work contributed to goals
3. **Show growth**: Demonstrate learning and development
4. **Acknowledge collaboration**: Credit team contributions
5. **Identify patterns**: Note trends and recurring themes

### Formatting Guidelines
1. **Consistent structure**: Follow template format
2. **Clear hierarchy**: Use headings and sections logically
3. **Visual clarity**: Use white space, bullets, and formatting
4. **Professional appearance**: Choose appropriate fonts and colors
5. **Accessibility**: Ensure content is readable and scannable

## Common Use Cases

### Performance Review Preparation
Create comprehensive summary of achievements for performance reviews, including:
- Key accomplishments and projects
- Goal achievement status
- Skills developed
- Impact and contributions
- Areas for growth

### Stakeholder Updates
Generate progress reports for stakeholders, focusing on:
- Project status and milestones
- Key decisions and outcomes
- Risks and mitigation strategies
- Resource needs
- Timeline updates

### Team Sync Reports
Produce regular team updates covering:
- Individual contributions
- Team accomplishments
- Cross-functional collaboration
- Blockers and support needs
- Upcoming priorities

### Career Documentation
Build career history documentation including:
- Role responsibilities
- Major projects and outcomes
- Skills and expertise gained
- Leadership and mentorship
- Recognition and awards

## Resources

This skill includes:

### references/
- **questions.md**: Question templates for gathering information
- **templates.md**: Structure templates for different report types
- **writing-guide.md**: Detailed guidance on content and style

### assets/
- **example-reports/**: Sample reports demonstrating best practices for each type

## Dependencies

This skill leverages existing Claude Code skills:
- **docx**: For creating Word documents
- **pptx**: For creating PowerPoint presentations

Ensure these skills are available when generating DOCX or PPTX reports.
