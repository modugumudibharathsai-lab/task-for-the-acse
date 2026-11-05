import React from "react";
import { cn } from "@/lib/utils";

// Renders inline markdown: **bold**, *italic*, `code`, and clean HTML entities/tags
function renderInline(text: string, keyPrefix: string): React.ReactNode[] {
  // Strip any stray HTML tags like <ul>, </ul>, <ol>, </ol>, <p>, </p>, <span>, </span>
  const cleaned = text
    .replace(/<\/?(ul|ol|p|span|div)[^>]*>/gi, "")
    .replace(/<br\s*\/?>/gi, " ");

  const nodes: React.ReactNode[] = [];
  // Pattern matches: **bold**, `code`, *italic*, and [link text](url)
  const pattern = /(\*\*(.+?)\*\*|`(.+?)`|\[(.+?)\]\((.+?)\)|\*([^*]+)\*)/g;
  let lastIndex = 0;
  let match: RegExpExecArray | null;
  let idx = 0;

  while ((match = pattern.exec(cleaned)) !== null) {
    if (match.index > lastIndex) {
      nodes.push(cleaned.slice(lastIndex, match.index));
    }
    if (match[2] !== undefined) {
      nodes.push(
        <strong key={`${keyPrefix}-b-${idx++}`} className="font-semibold text-foreground">
          {match[2]}
        </strong>
      );
    } else if (match[3] !== undefined) {
      nodes.push(
        <code
          key={`${keyPrefix}-c-${idx++}`}
          className="rounded bg-muted/80 px-1 py-0.5 font-mono text-[0.85em] text-foreground border border-border/40"
        >
          {match[3]}
        </code>
      );
    } else if (match[4] !== undefined && match[5] !== undefined) {
      nodes.push(
        <a
          key={`${keyPrefix}-a-${idx++}`}
          href={match[5]}
          target="_blank"
          rel="noopener noreferrer"
          className="text-primary underline underline-offset-2 hover:opacity-80 transition-opacity"
        >
          {match[4]}
        </a>
      );
    } else if (match[6] !== undefined) {
      nodes.push(
        <em key={`${keyPrefix}-i-${idx++}`} className="italic text-foreground/90">
          {match[6]}
        </em>
      );
    }
    lastIndex = pattern.lastIndex;
  }
  if (lastIndex < cleaned.length) {
    nodes.push(cleaned.slice(lastIndex));
  }
  return nodes;
}

// Renders the contents of a table cell, gracefully handling embedded <ul><li> or <br> tags
function renderCellContent(content: string, keyPrefix: string): React.ReactNode {
  const trimmed = content.trim();

  // Handle embedded HTML lists (e.g. <ul><li>Item 1</li><li>Item 2</li></ul>)
  if (/<li[^>]*>/i.test(trimmed)) {
    const liMatches = trimmed.match(/<li[^>]*>(.*?)<\/li>/gi);
    if (liMatches && liMatches.length > 0) {
      const items = liMatches.map((m) =>
        m.replace(/<\/?li[^>]*>/gi, "").replace(/<\/?(ul|ol|p|span)[^>]*>/gi, "").trim()
      );
      return (
        <div className="space-y-1 my-0.5">
          {items.map((item, idx) => (
            <div key={`${keyPrefix}-li-${idx}`} className="flex items-start gap-1.5 text-left">
              <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-primary/70" />
              <span className="leading-snug">{renderInline(item, `${keyPrefix}-li-txt-${idx}`)}</span>
            </div>
          ))}
        </div>
      );
    }
  }

  // Handle embedded <br> linebreaks
  if (/<br\s*\/?>/i.test(trimmed)) {
    const parts = trimmed.split(/<br\s*\/?>/gi).filter((p) => p.trim() !== "");
    return (
      <div className="space-y-1 my-0.5">
        {parts.map((part, idx) => {
          const bMatch = part.trim().match(/^[•\-*]\s*(.*)$/);
          if (bMatch) {
            return (
              <div key={`${keyPrefix}-br-${idx}`} className="flex items-start gap-1.5 text-left">
                <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-primary/70" />
                <span className="leading-snug">{renderInline(bMatch[1], `${keyPrefix}-br-txt-${idx}`)}</span>
              </div>
            );
          }
          return (
            <div key={`${keyPrefix}-br-${idx}`} className="leading-snug">
              {renderInline(part.trim(), `${keyPrefix}-br-txt-${idx}`)}
            </div>
          );
        })}
      </div>
    );
  }

  return <span className="leading-snug">{renderInline(trimmed, keyPrefix)}</span>;
}

interface TableBlock {
  type: "table";
  headers: string[];
  rows: string[][];
}

interface CodeBlock {
  type: "code";
  language: string;
  code: string;
}

interface HeadingBlock {
  type: "heading";
  level: number;
  content: string;
}

interface BulletBlock {
  type: "bullet";
  content: string;
}

interface NumberedBlock {
  type: "numbered";
  num: string;
  content: string;
}

interface HrBlock {
  type: "hr";
}

interface SpacerBlock {
  type: "spacer";
}

interface ParagraphBlock {
  type: "paragraph";
  content: string;
}

type Block =
  | TableBlock
  | CodeBlock
  | HeadingBlock
  | BulletBlock
  | NumberedBlock
  | HrBlock
  | SpacerBlock
  | ParagraphBlock;

export const MarkdownText: React.FC<{ text: string; className?: string }> = ({
  text,
  className,
}) => {
  if (!text) return null;

  const lines = text.split("\n");
  const blocks: Block[] = [];
  let i = 0;

  const isTableRow = (l: string) => /^\s*\|.*\|\s*$/.test(l);
  const isTableDelimiter = (l: string) => /^\s*\|(?:\s*:?-+:?\s*\|)+\s*$/.test(l);

  while (i < lines.length) {
    const line = lines[i];
    const trimmed = line.trim();

    // 1. Code Block: ```lang
    if (trimmed.startsWith("```")) {
      const language = trimmed.slice(3).trim();
      const codeLines: string[] = [];
      i++;
      while (i < lines.length && !lines[i].trim().startsWith("```")) {
        codeLines.push(lines[i]);
        i++;
      }
      i++; // consume closing ```
      blocks.push({
        type: "code",
        language,
        code: codeLines.join("\n"),
      });
      continue;
    }

    // 2. Markdown Table Detection:
    // Requires a header row starting and ending with '|', followed by a delimiter row '|---|---|'
    if (isTableRow(line) && i + 1 < lines.length && isTableDelimiter(lines[i + 1])) {
      const parseCells = (rowLine: string) =>
        rowLine
          .trim()
          .slice(1, -1)
          .split("|")
          .map((c) => c.trim());

      const headers = parseCells(lines[i]);
      i += 2; // skip header and delimiter rows

      const rows: string[][] = [];
      while (i < lines.length && isTableRow(lines[i])) {
        rows.push(parseCells(lines[i]));
        i++;
      }

      blocks.push({
        type: "table",
        headers,
        rows,
      });
      continue;
    }

    // 3. Headings: #, ##, ###
    const headingMatch = line.match(/^(#{1,4})\s+(.*)$/);
    if (headingMatch) {
      blocks.push({
        type: "heading",
        level: headingMatch[1].length,
        content: headingMatch[2],
      });
      i++;
      continue;
    }

    // 4. Horizontal Rule: ---, ***, ___
    if (/^\s*[-*_]{3,}\s*$/.test(line)) {
      blocks.push({ type: "hr" });
      i++;
      continue;
    }

    // 5. Spacer (empty line)
    if (trimmed === "") {
      blocks.push({ type: "spacer" });
      i++;
      continue;
    }

    // 6. Bullet Point
    const bulletMatch = line.match(/^\s*[•\-*]\s+(.*)$/);
    if (bulletMatch) {
      blocks.push({
        type: "bullet",
        content: bulletMatch[1],
      });
      i++;
      continue;
    }

    // 7. Numbered List Item
    const numberedMatch = line.match(/^\s*(\d+)\.\s+(.*)$/);
    if (numberedMatch) {
      blocks.push({
        type: "numbered",
        num: numberedMatch[1],
        content: numberedMatch[2],
      });
      i++;
      continue;
    }

    // 8. Raw HTML list item outside of table (e.g. <li>item</li>)
    const rawLiMatch = line.match(/^\s*<li[^>]*>(.*?)<\/li>\s*$/i);
    if (rawLiMatch) {
      blocks.push({
        type: "bullet",
        content: rawLiMatch[1],
      });
      i++;
      continue;
    }

    // 9. Standard Paragraph Line
    blocks.push({
      type: "paragraph",
      content: line,
    });
    i++;
  }

  return (
    <div className={cn("space-y-1.5 text-[13.5px] leading-relaxed", className)}>
      {blocks.map((block, idx) => {
        switch (block.type) {
          case "table":
            return (
              <div
                key={`tbl-${idx}`}
                className="my-2.5 overflow-x-auto rounded-lg border border-border/80 shadow-xs bg-card/60 backdrop-blur-xs"
              >
                <table className="w-full text-xs text-left border-collapse">
                  <thead>
                    <tr className="bg-muted/80 border-b border-border">
                      {block.headers.map((h, hIdx) => (
                        <th
                          key={`th-${idx}-${hIdx}`}
                          className="px-3.5 py-2 font-semibold text-foreground/90 tracking-wide uppercase text-sm"
                        >
                          {renderCellContent(h, `th-${idx}-${hIdx}`)}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-border/40">
                    {block.rows.map((row, rIdx) => (
                      <tr
                        key={`tr-${idx}-${rIdx}`}
                        className="hover:bg-muted/20 transition-colors"
                      >
                        {row.map((cell, cIdx) => (
                          <td
                            key={`td-${idx}-${rIdx}-${cIdx}`}
                            className="px-3.5 py-2 text-foreground/90 align-top"
                          >
                            {renderCellContent(cell, `td-${idx}-${rIdx}-${cIdx}`)}
                          </td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            );

          case "code":
            return (
              <div
                key={`code-${idx}`}
                className="my-2 overflow-x-auto rounded-md bg-slate-900 text-slate-100 p-3 font-mono text-xs shadow-inner"
              >
                <pre>{block.code}</pre>
              </div>
            );

          case "heading": {
            if (block.level === 1) {
              return (
                <h1
                  key={`h-${idx}`}
                  className="text-base font-bold text-foreground mt-3 mb-1 tracking-tight"
                >
                  {renderInline(block.content, `h1-${idx}`)}
                </h1>
              );
            }
            if (block.level === 2) {
              return (
                <h2
                  key={`h-${idx}`}
                  className="text-sm font-bold text-foreground mt-2.5 mb-1 tracking-tight"
                >
                  {renderInline(block.content, `h2-${idx}`)}
                </h2>
              );
            }
            return (
              <h3
                key={`h-${idx}`}
                className="text-xs font-bold text-foreground mt-2 mb-0.5 uppercase tracking-wider text-muted-foreground"
              >
                {renderInline(block.content, `h3-${idx}`)}
              </h3>
            );
          }

          case "bullet":
            return (
              <div key={`b-${idx}`} className="flex items-start gap-2 pl-1 my-0.5">
                <span className="mt-2 h-1.5 w-1.5 shrink-0 rounded-full bg-primary/70" />
                <span className="leading-snug">{renderInline(block.content, `b-txt-${idx}`)}</span>
              </div>
            );

          case "numbered":
            return (
              <div key={`num-${idx}`} className="flex items-start gap-2 pl-1 my-0.5">
                <span className="shrink-0 font-semibold text-muted-foreground text-xs">
                  {block.num}.
                </span>
                <span className="leading-snug">{renderInline(block.content, `num-txt-${idx}`)}</span>
              </div>
            );

          case "hr":
            return <hr key={`hr-${idx}`} className="my-2 border-border/60" />;

          case "spacer":
            return <div key={`sp-${idx}`} className="h-1" />;

          case "paragraph":
          default:
            return (
              <div key={`p-${idx}`} className="leading-relaxed">
                {renderInline(block.content, `p-txt-${idx}`)}
              </div>
            );
        }
      })}
    </div>
  );
};

