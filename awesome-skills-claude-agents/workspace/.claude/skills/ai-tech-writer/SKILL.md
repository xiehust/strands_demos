---
name: ai-tech-writer
description: Create high-quality AI technology articles for WeChat Official Accounts targeted at technical developers. Use this skill when the user requests creating AI/ML/LLM-related technical content, technology deep dives, model analysis, architecture explanations, or technical tutorials. Specializes in transforming complex AI concepts into well-structured technical articles with code examples, diagrams, and in-depth analysis.
---

# AI技术公众号创作Skill

## Overview

This skill empowers Claude to create professional AI technology articles for WeChat Official Accounts, specifically targeted at technical developers and AI practitioners. It provides comprehensive writing guidelines, technical concept references, and article structure templates to produce in-depth technical content.

**Target Audience**: Technical developers with programming background
**Article Focus**: Technical depth analysis with code examples and architecture diagrams
**Typical Word Count**: 1500-2500 words

## When to Use This Skill

Use this skill when the user requests:

- ✅ Creating AI/ML technology articles or blog posts
- ✅ Explaining AI concepts, algorithms, or architectures (e.g., Transformer, RAG, Agent)
- ✅ Analyzing new AI models or technology releases (e.g., GPT-4, Claude)
- ✅ Writing technical deep dives on LLM, NLP, Computer Vision topics
- ✅ Comparing different AI technologies or approaches
- ✅ Creating technical tutorials with code implementations
- ✅ Reverse engineering or analyzing AI system architectures

**Keywords to watch for**: 公众号文章, AI技术, 深度解析, 技术分析, 模型介绍, 架构设计, 代码实现, LLM, Transformer, Agent, RAG

## Core Capabilities

### 1. 📝 Professional Technical Writing

- **Technical depth**: In-depth analysis of AI architectures, algorithms, and implementations
- **Code-rich**: Complete, runnable code examples with detailed comments
- **Diagram integration**: Architecture diagrams, flowcharts, comparison tables
- **Reference-backed**: All claims supported by data sources and citations

### 2. 📚 Comprehensive AI Knowledge

- **Broad coverage**: From foundational ML to cutting-edge LLM technologies
- **Terminology precision**: Accurate use of technical terms with proper English/Chinese handling
- **Up-to-date**: Familiar with latest developments in AI field
- **Depth over breadth**: Focus on technical principles rather than superficial overviews

### 3. 🎨 Structured Content Organization

- **Template-based**: 5 article templates for different content types
- **Clear hierarchy**: Well-organized sections with logical flow
- **Progressive disclosure**: From high-level concepts to implementation details
- **Reader-friendly**: Balanced technical depth with readability

## How to Use This Skill

### Step 1: Understand the Requirements

When a user requests an AI technology article, clarify:

1. **Article type**: Deep dive? Model release analysis? Concept explanation? Technical comparison?
2. **Specific topic**: Which AI technology/model/concept to cover?
3. **Key focus**: Architecture? Implementation? Performance? Use cases?
4. **Reference materials**: Papers, documentation, URLs to reference

### Step 2: Load Relevant References

This skill includes three comprehensive reference files. Load them as needed:

#### `references/writing-style.md`
**When to load**: Always load this first for ANY article creation

**Contains**:
- Core writing principles for technical articles
- Standard article structure (1500-2500 words)
- Language style guidelines (professional but not stiff)
- Code example standards (complete, commented, following conventions)
- Diagram description requirements
- Terminology handling rules (Chinese/English usage)
- Common mistakes to avoid
- SEO and readability optimization

**Key sections**:
- Technical depth vs. readability balance
- Narrative structure (problem-driven, progressive)
- Code block requirements (completeness, comments, practicality)
- Diagram usage guidelines
- Data and citation standards

#### `references/ai-concepts.md`
**When to load**: When the article involves specific AI terminology or concepts

**Contains**:
- Comprehensive AI terminology database (10 major categories)
- 200+ terms with Chinese/English/abbreviation mappings
- Technical concept explanations
- Common technology stacks for different tasks
- Terminology usage recommendations

**Major categories**:
1. Machine Learning Basics
2. Neural Network Architectures
3. Natural Language Processing (NLP)
4. Large Language Models (LLM)
5. Retrieval-Augmented Generation (RAG)
6. AI Agents
7. Computer Vision (CV)
8. Multimodal AI
9. Model Evaluation & Benchmarks
10. Training Techniques

**Use this when**:
- Need to verify correct terminology
- Want to ensure consistent term usage
- Need to explain technical concepts
- Creating content about specific AI technologies

#### `references/article-templates.md`
**When to load**: When structuring the article

**Contains**:
- 5 detailed article templates with complete structures
- Word count allocation for each section
- Content requirements and examples
- Code snippet templates
- Diagram examples
- Writing workflow suggestions

**Templates available**:
1. **Technical Architecture Deep Dive** (2000-2500 words) ★★★★★
   - For analyzing AI systems, models, or framework architectures
   - Includes: Background → Architecture → Innovation → Performance → Best Practices

2. **New Technology/Model Release Analysis** (1500-2000 words) ★★★★☆
   - For interpreting newly released AI models or technologies
   - Includes: Announcement → Upgrades → Benchmarks → Usage Guide → Limitations

3. **Technical Principle/Concept Explanation** (1800-2200 words) ★★★★★
   - For deep dive into AI concepts, algorithms, or principles
   - Includes: Definition → Problem Background → Core Principles → Code Implementation → Applications

4. **Technical Practice Case Study** (1500-1800 words) ★★★★☆
   - For analyzing specific technical implementations or projects
   - Includes: Background → Tech Stack → Architecture → Core Implementation → Optimization

5. **Technology Comparison Review** (1500-2000 words) ★★★★☆
   - For comparing multiple technical solutions, models, or tools
   - Includes: Background → Overview → Multi-dimensional Comparison → Recommendations

### Step 3: Follow the Writing Process

1. **Select the appropriate template** from `article-templates.md` based on article type

2. **Apply writing guidelines** from `writing-style.md`:
   - Follow the standard article structure
   - Maintain professional yet accessible tone
   - Include complete, commented code examples
   - Add architecture diagrams and comparison tables
   - Use proper terminology (reference `ai-concepts.md`)

3. **Structure the article**:
   ```markdown
   # Compelling Technical Title (20-30 characters)

   ## Introduction (200-300 words)
   - Technical background and problem statement
   - Why this topic matters
   - What this article will cover

   ## [Main Body Sections] (1000-1500 words)
   - Technical principles with mathematical formulas
   - Architecture diagrams with explanations
   - Complete code implementations with comments
   - Performance analysis with data

   ## Summary & Outlook (100-200 words)
   - Key takeaways (3-5 bullet points)
   - Future directions
   - Actionable recommendations

   ## References
   - Papers, documentation, benchmarks
   ```

4. **Ensure technical quality**:
   - All code examples must be complete and runnable
   - Include necessary import statements
   - Add clear Chinese comments for key steps
   - Provide usage examples and expected output

5. **Add visual elements**:
   - Architecture diagrams (ASCII art or description)
   - Comparison tables
   - Flowcharts for algorithms
   - Performance charts (when applicable)

### Step 4: Quality Checklist

Before finalizing the article, verify:

- ✅ **Technical accuracy**: Code runs correctly, data has sources
- ✅ **Logical coherence**: Smooth transitions between sections
- ✅ **Proper terminology**: Consistent use of Chinese/English terms
- ✅ **Complete structure**: Introduction, body, conclusion, references all present
- ✅ **Code quality**: Complete, commented, follows conventions
- ✅ **Diagrams included**: Architecture/flow diagrams where appropriate
- ✅ **Word count**: Within target range (1500-2500 words)
- ✅ **References cited**: All data and claims have sources

## Example Usage Scenarios

### Scenario 1: Technical Architecture Analysis

**User Request**: "帮我写一篇关于Transformer架构的深度解析文章"

**Workflow**:
1. Load `references/writing-style.md` for writing guidelines
2. Load `references/article-templates.md` → Select "Template 1: Technical Architecture Deep Dive"
3. Load `references/ai-concepts.md` → Reference NLP and Transformer terminology
4. Structure the article following the template:
   - Introduction: Transformer background and importance
   - Technical Background: Evolution from RNN → LSTM → Attention → Transformer
   - Core Architecture: Self-Attention mechanism with mathematical formulas
   - Code Implementation: Complete Multi-Head Attention implementation
   - Innovation Analysis: Key innovations and performance improvements
   - Summary: Key takeaways and recommendations
5. Include:
   - Architecture diagram of Transformer
   - Mathematical derivation of Self-Attention
   - Complete Python code with detailed comments
   - Performance comparison table (Transformer vs RNN/LSTM)

### Scenario 2: New Model Release Analysis

**User Request**: "Claude发布了新模型，帮我写篇技术分析文章"

**Workflow**:
1. Load `references/writing-style.md`
2. Load `references/article-templates.md` → Select "Template 2: New Technology/Model Release Analysis"
3. Gather information about the new model (via web search or provided materials)
4. Structure the article:
   - Major Release: Announcement and key highlights
   - Core Tech Upgrades: New features and improvements with comparison table
   - Benchmark Performance: Test results on various benchmarks
   - Usage Experience: API examples and prompt engineering tips
   - Limitations: Known issues and improvement areas
5. Include:
   - Feature comparison table (old vs new)
   - Benchmark test results
   - API usage code examples
   - Cost and performance trade-off analysis

### Scenario 3: Concept Deep Dive

**User Request**: "写一篇详细讲解RAG（检索增强生成）技术原理的文章"

**Workflow**:
1. Load `references/writing-style.md`
2. Load `references/article-templates.md` → Select "Template 3: Technical Principle/Concept Explanation"
3. Load `references/ai-concepts.md` → Reference RAG terminology
4. Structure the article:
   - What is RAG: Definition and importance
   - Problem Background: Why LLMs need RAG
   - Core Principles: Retrieval + Generation pipeline
   - Math & Implementation: Vector search, similarity calculation
   - Code Implementation: Complete RAG system with LangChain
   - Applications: Use cases and best practices
5. Include:
   - RAG architecture diagram
   - Vector similarity calculation formulas
   - Complete implementation code
   - Performance comparison (with/without RAG)

## Writing Style Guidelines Summary

### Language Tone
- **Professional but accessible**: Use accurate technical terms but explain complex concepts
- **Objective and data-driven**: Base claims on facts, benchmarks, and research
- **Avoid marketing language**: No exaggerated claims like "最强" (strongest), "颠覆" (revolutionary)

### Technical Terminology
- **First mention**: Chinese (English), e.g., "检索增强生成（RAG）"
- **Subsequent use**: Prefer English for technical terms, e.g., "RAG", "Transformer"
- **Common abbreviations**: Use directly: NLP, LLM, API, GPU

### Code Examples
- **Completeness**: Include all necessary imports and context
- **Comments**: Add clear Chinese comments for key steps
- **Conventions**: Follow language standards (PEP 8 for Python)
- **Practicality**: Use realistic examples, not toy code

### Visual Elements
- **Architecture diagrams**: ASCII art or detailed descriptions
- **Flowcharts**: For algorithms and processes
- **Comparison tables**: For technology/performance comparisons
- **Data charts**: For benchmark results (described textually)

## Common Mistakes to Avoid

- ❌ Overly marketing-oriented language
- ❌ Incomplete code examples missing imports or context
- ❌ Technical details without explanation
- ❌ Diagrams without accompanying text explanations
- ❌ Inconsistent terminology usage
- ❌ Claims without data sources or citations
- ❌ Superficial content without technical depth

## Output Format

Save the final article as a Markdown file (`.md`) with:
- Clear heading hierarchy (h1 for title, h2 for sections, h3 for subsections)
- Properly formatted code blocks with language specification
- Tables for comparisons
- Numbered or bulleted lists for key points
- Reference section at the end

## Notes

- **Priority**: Technical depth and accuracy over simplification
- **Audience**: Assume readers have programming background and basic AI knowledge
- **Length**: Aim for 1500-2500 words for comprehensive coverage
- **Time**: If analyzing recent developments, note the data timestamp
- **Sources**: Always cite papers, documentation, and benchmark sources

---

**Remember**: The goal is to create articles that technical developers can learn from and apply in practice. Focus on explaining the "why" and "how", not just the "what".
