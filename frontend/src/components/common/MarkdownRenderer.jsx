import React from 'react';

/**
 * Clean, zero-dependency Markdown renderer for LLM customer support responses.
 * Parses bold, italics, inline code, fenced code blocks, lists, headings, and paragraphs.
 */
export function MarkdownRenderer({ content = '', className = '' }) {
  if (!content) return null;

  // Split into lines to identify block elements
  const lines = content.split('\n');
  const elements = [];
  let inCodeBlock = false;
  let codeBlockContent = [];
  let currentList = [];
  let listType = null; // 'ul' or 'ol'

  const flushList = () => {
    if (currentList.length > 0) {
      if (listType === 'ol') {
        elements.push(
          <ol key={`ol-${elements.length}`} className="list-decimal pl-5 space-y-1.5 my-2 text-slate-200">
            {currentList.map((item, idx) => (
              <li key={idx} className="leading-relaxed">
                {parseInline(item)}
              </li>
            ))}
          </ol>
        );
      } else {
        elements.push(
          <ul key={`ul-${elements.length}`} className="list-disc pl-5 space-y-1.5 my-2 text-slate-200">
            {currentList.map((item, idx) => (
              <li key={idx} className="leading-relaxed">
                {parseInline(item)}
              </li>
            ))}
          </ul>
        );
      }
      currentList = [];
      listType = null;
    }
  };

  // Helper to parse inline markdown (bold, italic, code)
  const parseInline = (text) => {
    if (!text) return null;

    // Pattern matching tokens: `code`, **bold**, *italic*
    const parts = [];
    let remaining = text;
    let keyIdx = 0;

    // Regex for inline code `...`, bold **...**, or *...*
    const tokenRegex = /(`([^`]+)`|\*\*([^*]+)\*\*|\*([^*]+)\*)/;

    while (remaining.length > 0) {
      const match = remaining.match(tokenRegex);
      if (!match) {
        parts.push(remaining);
        break;
      }

      const matchIndex = match.index;
      if (matchIndex > 0) {
        parts.push(remaining.substring(0, matchIndex));
      }

      const matchedString = match[0];
      if (matchedString.startsWith('`')) {
        // Inline code
        parts.push(
          <code
            key={`code-${keyIdx++}`}
            className="px-1.5 py-0.5 rounded bg-violet-950/40 text-violet-300 font-mono text-[11px] border border-violet-500/20"
          >
            {match[2]}
          </code>
        );
      } else if (matchedString.startsWith('**')) {
        // Bold
        parts.push(
          <strong key={`bold-${keyIdx++}`} className="font-bold text-white">
            {match[3]}
          </strong>
        );
      } else if (matchedString.startsWith('*')) {
        // Italic
        parts.push(
          <em key={`em-${keyIdx++}`} className="italic text-slate-300">
            {match[4]}
          </em>
        );
      }

      remaining = remaining.substring(matchIndex + matchedString.length);
    }

    return parts;
  };

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    const trimmed = line.trim();

    // Fenced code blocks
    if (trimmed.startsWith('```')) {
      if (inCodeBlock) {
        // Close code block
        elements.push(
          <pre
            key={`codeblock-${elements.length}`}
            className="p-3 my-2.5 rounded-xl bg-[#0B1020] border border-white/10 text-violet-300 font-mono text-xs overflow-x-auto leading-relaxed"
          >
            <code>{codeBlockContent.join('\n')}</code>
          </pre>
        );
        codeBlockContent = [];
        inCodeBlock = false;
      } else {
        flushList();
        inCodeBlock = true;
      }
      continue;
    }

    if (inCodeBlock) {
      codeBlockContent.push(line);
      continue;
    }

    // Unordered List (- item or * item)
    const ulMatch = trimmed.match(/^[-*]\s+(.+)$/);
    if (ulMatch) {
      if (listType !== 'ul') {
        flushList();
        listType = 'ul';
      }
      currentList.push(ulMatch[1]);
      continue;
    }

    // Ordered List (1. item)
    const olMatch = trimmed.match(/^\d+\.\s+(.+)$/);
    if (olMatch) {
      if (listType !== 'ol') {
        flushList();
        listType = 'ol';
      }
      currentList.push(olMatch[1]);
      continue;
    }

    // Flush any pending list if we hit non-list line
    flushList();

    // Headings
    if (trimmed.startsWith('### ')) {
      elements.push(
        <h4 key={`h4-${elements.length}`} className="text-sm font-bold text-white mt-3 mb-1.5 flex items-center space-x-1.5">
          <span>{parseInline(trimmed.substring(4))}</span>
        </h4>
      );
      continue;
    }
    if (trimmed.startsWith('## ')) {
      elements.push(
        <h3 key={`h3-${elements.length}`} className="text-base font-bold text-white mt-3.5 mb-1.5">
          {parseInline(trimmed.substring(3))}
        </h3>
      );
      continue;
    }
    if (trimmed.startsWith('# ')) {
      elements.push(
        <h2 key={`h2-${elements.length}`} className="text-lg font-bold text-white mt-4 mb-2">
          {parseInline(trimmed.substring(2))}
        </h2>
      );
      continue;
    }

    // Blank line
    if (trimmed === '') {
      continue;
    }

    // Regular paragraph
    elements.push(
      <p key={`p-${elements.length}`} className="my-1.5 leading-relaxed text-slate-200">
        {parseInline(line)}
      </p>
    );
  }

  // Final flush for trailing list or code block
  flushList();
  if (inCodeBlock && codeBlockContent.length > 0) {
    elements.push(
      <pre
        key={`codeblock-${elements.length}`}
        className="p-3 my-2.5 rounded-xl bg-[#0B1020] border border-white/10 text-violet-300 font-mono text-xs overflow-x-auto leading-relaxed"
      >
        <code>{codeBlockContent.join('\n')}</code>
      </pre>
    );
  }

  return <div className={`space-y-1 ${className}`}>{elements}</div>;
}

export default MarkdownRenderer;

