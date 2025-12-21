---
name: student-analyzer
description: Comprehensive student note analysis and optimization system for evaluating learning comprehension and enhancing note quality. Use this skill when students upload study notes for analysis, when assessing knowledge mastery from note content, when optimizing note structure and completeness, or when generating personalized learning recommendations based on note quality and understanding depth. Handles text files, markdown, PDFs, and document formats containing student notes.
---

# Student Analyzer

## Overview

This skill provides a systematic workflow for analyzing student learning notes, identifying knowledge gaps, optimizing note structure, and generating personalized learning recommendations. It combines note content analysis with pedagogical best practices to help students improve their understanding and study materials.

## Workflow

When a student uploads learning notes, follow this sequential workflow:

### Step 1: Accept and Parse Note Content

**Objective**: Receive and understand the note structure and content.

**Process**:
1. Identify the file format (text, markdown, PDF, DOCX)
2. Extract full text content while preserving structure (headings, lists, emphasis)
3. Identify the subject/topic from note content or filename
4. Note the approximate length and organization level

**Example**:
```
User: "Here are my biology notes from today's class on cell division"
→ Read the file, identify it's about cell division/mitosis
→ Extract headings, bullet points, diagrams descriptions
→ Note: "Biology - Cell Division, ~2 pages, partially structured"
```

### Step 2: Extract Key Knowledge Points

**Objective**: Identify core concepts and their relationships from the notes.

**Process**:
1. Identify main topics and subtopics covered
2. Extract key terms, definitions, and concepts
3. Recognize relationships between concepts (cause-effect, hierarchical, sequential)
4. Note any examples, formulas, or important details provided
5. Identify what concepts the student emphasized (repeated, underlined, etc.)

**Output Format**:
```markdown
## Knowledge Points Identified
1. **Main Topic 1**: [Concept name]
   - Key details: [Summary]
   - Student emphasis: [High/Medium/Low]

2. **Main Topic 2**: [Concept name]
   - Key details: [Summary]
   - Related to: [Topic 1]
```

### Step 3: Optimize Note Structure

**Objective**: Identify missing concepts and improve organization.

**Process**:
1. **Identify gaps**: Compare extracted knowledge points against expected curriculum
   - Missing foundational concepts
   - Incomplete explanations
   - Missing connections between topics

2. **Improve structure**:
   - Suggest clear hierarchical organization
   - Add section headings if missing
   - Recommend grouping related concepts
   - Propose summary sections

3. **Enhance content**:
   - Add brief explanations for incomplete concepts
   - Suggest mnemonic devices for memorization
   - Recommend visual aids (diagrams, tables, flowcharts)
   - Add practice questions or self-check items

**Example additions**:
```markdown
## Suggested Additions

### Missing Concepts
- **Cytokinesis**: The notes cover mitosis phases but don't mention cytokinesis,
  the final step where the cell physically divides.

### Structural Improvements
- Group prophase, metaphase, anaphase, telophase under "Mitosis Phases" heading
- Add a comparison table: Mitosis vs. Meiosis
- Create a summary section with key takeaways

### Enhancement Suggestions
- Mnemonic for phases: "PMAT" (Prophase, Metaphase, Anaphase, Telophase)
- Add diagram: Chromosome movement during each phase
- Self-check: "Can you explain what happens to chromosomes in each phase?"
```

### Step 4: Assess Knowledge Understanding

**Objective**: Evaluate the student's comprehension level for each concept.

**Assessment Criteria**:
- **Mastered (90-100%)**: Accurate details, connections explained, examples provided
- **Good Understanding (70-89%)**: Core concept grasped, minor gaps in details
- **Partial Understanding (50-69%)**: Basic idea present, missing key details or relationships
- **Needs Review (<50%)**: Incomplete, inaccurate, or missing entirely

**Process**:
1. For each major concept, rate understanding level
2. Note indicators:
   - Accuracy of definitions
   - Completeness of explanations
   - Presence of examples or applications
   - Connections to related concepts
   - Depth of detail provided

**Output Format**:
```markdown
## Understanding Assessment

| Concept | Level | Evidence | Recommendation |
|---------|-------|----------|----------------|
| Mitosis Phases | Good (75%) | All phases listed, missing some details about chromosome behavior | Review metaphase and anaphase specifics |
| Cell Cycle | Partial (60%) | Mentioned but not explained in depth | Study G1, S, G2 phases and their purposes |
| Cytokinesis | Needs Review (0%) | Not mentioned in notes | Add this section - it's essential for complete understanding |
```

### Step 5: Generate Optimized Notes and Recommendations

**Objective**: Produce enhanced notes and a personalized study plan.

**Deliverables**:

1. **Optimized Notes Document**:
   - Reorganized structure with clear headings
   - Filled-in missing concepts (clearly marked as additions)
   - Enhanced with mnemonics, tables, or diagram suggestions
   - Added self-check questions

2. **Learning Recommendations**:
   ```markdown
   ## Personalized Study Recommendations

   ### Priority Areas (Focus Here First)
   1. **Cytokinesis** - Not covered in your notes but essential
      - Action: Read textbook section 8.3, watch Khan Academy video
      - Time: 20 minutes

   ### Strengthen Understanding
   2. **Cell Cycle Phases** - You have the basics, need more depth
      - Action: Create a detailed timeline diagram showing G1→S→G2→M
      - Time: 15 minutes

   ### Practice and Reinforce
   3. **Mitosis Phase Identification** - Good foundation, practice application
      - Action: Use flashcards, label diagram practice problems
      - Time: 30 minutes

   ### Study Techniques for This Topic
   - Use the PMAT mnemonic for mitosis phases
   - Draw diagrams repeatedly from memory
   - Create a comparison table for mitosis vs. meiosis
   - Teach the concept to someone else

   ### Estimated Study Time: 1-2 hours
   ```

## Output Example

When complete, provide:

1. **Analysis Summary**: Brief overview of note quality and main gaps
2. **Optimized Notes**: Enhanced version with additions clearly marked
3. **Understanding Assessment**: Table showing comprehension levels
4. **Study Plan**: Prioritized recommendations with time estimates

## Best Practices

- **Be encouraging**: Acknowledge what the student did well
- **Be specific**: Give concrete actions, not vague advice
- **Be realistic**: Estimate appropriate time commitments
- **Be pedagogical**: Suggest active learning techniques (drawing, teaching, practice)
- **Mark additions clearly**: Use [ADDED], italics, or different formatting so students know what they missed
- **Respect learning styles**: Suggest visual, verbal, and kinesthetic approaches

## Handling Different Note Types

### Minimal Notes (< 1 page)
- Focus on filling content gaps
- Provide extensive additions
- Recommend comprehensive review

### Comprehensive Notes (> 5 pages)
- Focus on organization and structure
- Add connections and summaries
- Recommend practice problems

### Unstructured Notes (no headings, stream of consciousness)
- Prioritize restructuring
- Extract and organize main points
- Teach note-taking framework

### Advanced Notes (beyond expected level)
- Acknowledge depth
- Suggest extension topics
- Recommend teaching others or advanced applications
