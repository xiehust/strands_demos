import { useEffect, useRef, useState, memo } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import mermaid from 'mermaid';
import hljs from 'highlight.js';

// Initialize mermaid with dark theme
mermaid.initialize({
  startOnLoad: false,
  theme: 'dark',
  themeVariables: {
    primaryColor: '#2b6cee',
    primaryTextColor: '#ffffff',
    primaryBorderColor: '#3d4f6f',
    lineColor: '#9da6b9',
    secondaryColor: '#1a1f2e',
    tertiaryColor: '#101622',
    background: '#1a1f2e',
    mainBkg: '#1a1f2e',
    nodeBorder: '#3d4f6f',
    clusterBkg: '#101622',
    titleColor: '#ffffff',
    edgeLabelBackground: '#1a1f2e',
  },
  fontFamily: 'Space Grotesk, sans-serif',
});

interface MarkdownRendererProps {
  content: string;
  className?: string;
}

// Mermaid diagram component
const MermaidDiagram = memo(function MermaidDiagram({ chart }: { chart: string }) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [svg, setSvg] = useState<string>('');
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const renderDiagram = async () => {
      if (!chart.trim()) return;

      try {
        const id = `mermaid-${Math.random().toString(36).substring(2, 11)}`;
        const { svg: renderedSvg } = await mermaid.render(id, chart);
        setSvg(renderedSvg);
        setError(null);
      } catch (err) {
        console.error('Mermaid rendering error:', err);
        setError(err instanceof Error ? err.message : 'Failed to render diagram');
      }
    };

    renderDiagram();
  }, [chart]);

  if (error) {
    return (
      <div className="bg-status-error/10 border border-status-error/30 rounded-lg p-4 my-4">
        <div className="flex items-center gap-2 text-status-error mb-2">
          <span className="material-symbols-outlined text-sm">error</span>
          <span className="text-sm font-medium">Mermaid Diagram Error</span>
        </div>
        <pre className="text-xs text-muted overflow-x-auto">{error}</pre>
        <details className="mt-2">
          <summary className="text-xs text-muted cursor-pointer hover:text-white">Show source</summary>
          <pre className="text-xs text-muted mt-2 overflow-x-auto">{chart}</pre>
        </details>
      </div>
    );
  }

  if (!svg) {
    return (
      <div className="flex items-center justify-center p-4 my-4 bg-dark-card border border-dark-border rounded-lg">
        <span className="text-muted text-sm">Loading diagram...</span>
      </div>
    );
  }

  return (
    <div
      ref={containerRef}
      className="my-4 p-4 bg-dark-card border border-dark-border rounded-lg overflow-x-auto flex justify-center"
      dangerouslySetInnerHTML={{ __html: svg }}
    />
  );
});

// Code block component with syntax highlighting and copy button
const CodeBlock = memo(function CodeBlock({
  language,
  children,
}: {
  language?: string;
  children: string;
}) {
  const [copied, setCopied] = useState(false);
  const codeRef = useRef<HTMLElement>(null);

  // Check if this is a mermaid diagram
  if (language === 'mermaid') {
    return <MermaidDiagram chart={children} />;
  }

  // Apply syntax highlighting
  useEffect(() => {
    if (codeRef.current && language) {
      // Reset previous highlighting
      codeRef.current.removeAttribute('data-highlighted');
      try {
        hljs.highlightElement(codeRef.current);
      } catch (err) {
        console.error('Highlight error:', err);
      }
    }
  }, [children, language]);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(children);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy:', err);
    }
  };

  return (
    <div className="relative my-4 bg-dark-card border border-dark-border rounded-lg overflow-hidden group">
      {/* Header with language label and copy button */}
      <div className="flex items-center justify-between px-4 py-2 bg-dark-hover border-b border-dark-border">
        <span className="text-xs text-muted font-medium uppercase tracking-wider">
          {language || 'code'}
        </span>
        <button
          onClick={handleCopy}
          className="flex items-center gap-1 px-2 py-1 text-xs text-muted hover:text-white bg-dark-card hover:bg-dark-border rounded transition-colors"
        >
          <span className="material-symbols-outlined text-sm">
            {copied ? 'check' : 'content_copy'}
          </span>
          {copied ? 'Copied!' : 'Copy'}
        </button>
      </div>
      {/* Code content with syntax highlighting */}
      <pre className="p-4 overflow-x-auto">
        <code
          ref={codeRef}
          className={`text-sm font-mono ${language ? `language-${language}` : ''}`}
        >
          {children}
        </code>
      </pre>
    </div>
  );
});

// Inline code component
const InlineCode = memo(function InlineCode({ children }: { children: React.ReactNode }) {
  return (
    <code className="px-1.5 py-0.5 bg-dark-card border border-dark-border rounded text-sm text-primary font-mono">
      {children}
    </code>
  );
});

export default function MarkdownRenderer({ content, className = '' }: MarkdownRendererProps) {
  return (
    <div className={`markdown-content ${className}`}>
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
          // Headers
          h1: ({ children }) => (
            <h1 className="text-2xl font-bold text-white mt-6 mb-4 pb-2 border-b border-dark-border">
              {children}
            </h1>
          ),
          h2: ({ children }) => (
            <h2 className="text-xl font-bold text-white mt-5 mb-3">{children}</h2>
          ),
          h3: ({ children }) => (
            <h3 className="text-lg font-semibold text-white mt-4 mb-2">{children}</h3>
          ),
          h4: ({ children }) => (
            <h4 className="text-base font-semibold text-white mt-3 mb-2">{children}</h4>
          ),
          h5: ({ children }) => (
            <h5 className="text-sm font-semibold text-white mt-2 mb-1">{children}</h5>
          ),
          h6: ({ children }) => (
            <h6 className="text-sm font-medium text-muted mt-2 mb-1">{children}</h6>
          ),

          // Paragraphs
          p: ({ children }) => <p className="text-white mb-4 leading-relaxed">{children}</p>,

          // Links
          a: ({ href, children }) => (
            <a
              href={href}
              target="_blank"
              rel="noopener noreferrer"
              className="text-primary hover:text-primary-hover underline decoration-primary/50 hover:decoration-primary transition-colors"
            >
              {children}
            </a>
          ),

          // Lists
          ul: ({ children }) => (
            <ul className="list-disc list-inside mb-4 space-y-1 text-white">{children}</ul>
          ),
          ol: ({ children }) => (
            <ol className="list-decimal list-inside mb-4 space-y-1 text-white">{children}</ol>
          ),
          li: ({ children }) => <li className="text-white leading-relaxed">{children}</li>,

          // Blockquote
          blockquote: ({ children }) => (
            <blockquote className="border-l-4 border-primary pl-4 my-4 text-muted italic">
              {children}
            </blockquote>
          ),

          // Code blocks
          code: ({ className, children }) => {
            const match = /language-(\w+)/.exec(className || '');
            const isInline = !match && !className;
            const codeContent = String(children).replace(/\n$/, '');

            if (isInline) {
              return <InlineCode>{children}</InlineCode>;
            }

            return <CodeBlock language={match?.[1]} children={codeContent} />;
          },

          // Pre tag (wrapper for code blocks)
          pre: ({ children }) => <>{children}</>,

          // Tables
          table: ({ children }) => (
            <div className="overflow-x-auto my-4">
              <table className="min-w-full border border-dark-border rounded-lg overflow-hidden">
                {children}
              </table>
            </div>
          ),
          thead: ({ children }) => <thead className="bg-dark-hover">{children}</thead>,
          tbody: ({ children }) => <tbody className="divide-y divide-dark-border">{children}</tbody>,
          tr: ({ children }) => <tr className="hover:bg-dark-hover transition-colors">{children}</tr>,
          th: ({ children }) => (
            <th className="px-4 py-3 text-left text-sm font-semibold text-white border-b border-dark-border">
              {children}
            </th>
          ),
          td: ({ children }) => (
            <td className="px-4 py-3 text-sm text-muted">{children}</td>
          ),

          // Horizontal rule
          hr: () => <hr className="my-6 border-dark-border" />,

          // Images
          img: ({ src, alt }) => (
            <img
              src={src}
              alt={alt || ''}
              className="max-w-full h-auto my-4 rounded-lg border border-dark-border"
            />
          ),

          // Strong/Bold
          strong: ({ children }) => <strong className="font-semibold text-white">{children}</strong>,

          // Emphasis/Italic
          em: ({ children }) => <em className="italic">{children}</em>,

          // Strikethrough
          del: ({ children }) => <del className="line-through text-muted">{children}</del>,

          // Task list items (GFM)
          input: ({ checked }) => (
            <input
              type="checkbox"
              checked={checked}
              readOnly
              className="mr-2 rounded border-dark-border bg-dark-card text-primary focus:ring-primary"
            />
          ),
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  );
}
