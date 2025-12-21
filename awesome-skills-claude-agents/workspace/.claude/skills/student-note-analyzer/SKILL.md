---
name: student-note-analyzer
description: Comprehensive student note analysis and optimization system for evaluating learning comprehension and enhancing note quality. Use this skill when students upload study notes for analysis, when assessing knowledge mastery from note content, when optimizing note structure and completeness, or when generating personalized learning recommendations based on note quality and understanding depth. Handles text files, markdown, PDFs, and document formats containing student notes.
---

# Student Note Analyzer

Analyze student notes to assess knowledge mastery, identify gaps, optimize structure, and provide personalized learning recommendations.

## Workflow

### Step 1: Receive and Parse Notes

**Accept these formats:**
- Text files (.txt)
- Markdown (.md)
- PDF documents (.pdf)
- Word documents (.docx)
- Images with text (OCR if needed)

**Initial parsing:**
1. Read the complete note content
2. Identify the subject/topic being covered
3. Extract the note structure (headings, sections, lists)
4. Note any student annotations, questions, or highlights

### Step 2: Analyze Note Content

**Extract knowledge points using criteria from [analysis_framework.md](references/analysis_framework.md):**

1. **Identify primary knowledge points:**
   - Core definitions and concepts
   - Key principles or theories
   - Important processes or procedures
   - Critical relationships between concepts
   - Practical applications or examples

2. **Identify secondary knowledge points:**
   - Supporting details and evidence
   - Contextual information
   - Comparisons and contrasts
   - Exceptions or special cases

3. **Assess note structure:**
   - Organization and logical flow
   - Use of hierarchy (headings, bullets)
   - Visual aids or diagrams
   - Cross-references between topics
   - Personal annotations or questions

**Consider classroom context:**
- If curriculum information is available, compare notes against expected content
- Identify topics that should be present but are missing
- Note depth of coverage for each topic

### Step 3: Evaluate Understanding Level

**Assess mastery for each knowledge point using the 4-level framework:**

**Level 1 - Recognition (Basic):**
- Notes show verbatim copying
- Minimal personal interpretation
- No examples or applications
- Lists without explanation

**Level 2 - Comprehension (Developing):**
- Concepts restated in student's words
- Basic examples provided
- Simple connections made
- Main ideas understood

**Level 3 - Application (Proficient):**
- Concepts applied to scenarios
- Original examples created
- Patterns identified
- Meaningful questions asked

**Level 4 - Analysis (Advanced):**
- Multiple concepts compared
- Critical evaluation present
- Information synthesized
- Independent conclusions drawn

**Document evidence:** For each assessed topic, note specific examples from the notes that demonstrate the understanding level.

### Step 4: Optimize Notes

**Enhancement priorities:**

1. **Fill knowledge gaps:**
   - Add missing key concepts from curriculum
   - Provide definitions for undefined terms
   - Include important context or background
   - Add connections between isolated topics

2. **Improve structure:**
   - Reorganize for logical flow
   - Add clear hierarchical headings
   - Create visual structure (tables, lists, diagrams)
   - Insert cross-references between related sections

3. **Enhance clarity:**
   - Expand unclear explanations
   - Add concrete examples for abstract concepts
   - Include visual representations where helpful
   - Highlight critical information

4. **Maintain student voice:**
   - Preserve original insights and annotations
   - Build upon existing understanding
   - Clearly distinguish additions from original content
   - Keep personal examples and questions

**Use the optimized notes template:** See [assets/optimized_notes_template.md](assets/optimized_notes_template.md) for structure.

### Step 5: Generate Learning Recommendations

**Create personalized recommendations based on:**

1. **Overall assessment:**
   - Determine predominant understanding level
   - Identify strengths and growth areas
   - Recognize effective study patterns

2. **Topic-by-topic mastery:**
   - Rate each major topic (4-star scale)
   - Provide evidence from notes
   - Give specific next steps

3. **Priority actions:**
   - Immediate focus (1-2 days)
   - Short-term goals (1 week)
   - Long-term development

4. **Study strategy insights:**
   - Effective techniques observed
   - Suggested improvements
   - Practice and review plan

**Use the recommendations template:** See [assets/learning_recommendations_template.md](assets/learning_recommendations_template.md) for structure.

## Output Format

**Always provide two documents:**

1. **Optimized Notes** - Enhanced version of student's notes with:
   - Original content preserved and clearly marked
   - Missing concepts added with explanations
   - Improved structure and organization
   - Visual aids and connections
   - Summary and key takeaways

2. **Learning Recommendations** - Personalized guidance including:
   - Overall understanding assessment
   - Topic-by-topic mastery ratings
   - Priority learning actions
   - Study strategy recommendations
   - Practice exercises and review plan
   - Resources for further learning

## Best Practices

**Analysis quality:**
- Be thorough but focused on actionable insights
- Use specific evidence from the notes
- Balance encouragement with constructive guidance
- Tailor recommendations to observed learning patterns

**Tone and approach:**
- Supportive and encouraging
- Specific rather than generic
- Action-oriented
- Growth-mindset focused

**Optimization guidelines:**
- Enhance, don't replace student's work
- Preserve student's voice and insights
- Make additions clearly distinguishable
- Focus on high-impact improvements

## Example Usage

**User request:** "Please analyze my biology notes on cellular respiration"

**Process:**
1. Read and parse the uploaded notes
2. Identify knowledge points: glycolysis, Krebs cycle, electron transport chain, ATP production
3. Assess understanding level for each process
4. Note gaps (e.g., missing regulation mechanisms)
5. Create optimized notes with added context
6. Generate recommendations prioritizing weak areas

**Output:** Two documents with enhanced notes and personalized learning plan.

## Reference Materials

- **[analysis_framework.md](references/analysis_framework.md)**: Detailed criteria for knowledge point identification and understanding assessment levels

## Templates

- **[optimized_notes_template.md](assets/optimized_notes_template.md)**: Structure for enhanced notes output
- **[learning_recommendations_template.md](assets/learning_recommendations_template.md)**: Format for personalized guidance
