import { useState, useMemo } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { X, ChevronRight, FileText, Search, Highlighter } from 'lucide-react';

export interface DocumentSection {
  id: string;
  title: string;
  level: number;
}

interface DocumentPreviewProps {
  title: string;
  content: string;
  onClose?: () => void;
  highlightQuery?: string;
}

export function DocumentPreview({ title, content, onClose, highlightQuery }: DocumentPreviewProps) {
  const [activeSection, setActiveSection] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');

  const sections = useMemo((): DocumentSection[] => {
    const regex = /^(#{1,3})\s+(.+)$/gm;
    const matches: DocumentSection[] = [];
    let match;
    
    while ((match = regex.exec(content)) !== null) {
      const level = match[1].length;
      const sectionTitle = match[2].trim();
      const id = sectionTitle.toLowerCase().replace(/[^a-z0-9]+/g, '-');
      
      matches.push({ id, title: sectionTitle, level });
    }
    
    return matches;
  }, [content]);

  const scrollToSection = (id: string) => {
    const element = document.getElementById(id);
    if (element) {
      element.scrollIntoView({ behavior: 'smooth', block: 'start' });
      setActiveSection(id);
    }
  };

  const highlightContent = useMemo(() => {
    if (!highlightQuery) return content;
    
    const escaped = highlightQuery.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    const regex = new RegExp(`(${escaped})`, 'gi');
    return content.replace(regex, '<mark class="bg-yellow-200 px-0.5 rounded">$1</mark>');
  }, [content, highlightQuery]);

  const handleContentClick = () => {
    setSearchQuery('');
  };

  return (
    <div className="h-full flex flex-col bg-white rounded-xl shadow-lg overflow-hidden">
      <div className="flex items-center justify-between px-4 py-3 border-b border-gray-200 bg-gray-50">
        <div className="flex items-center gap-3">
          <FileText className="w-5 h-5 text-primary-500" />
          <h2 className="font-semibold text-gray-800 truncate flex-1">{title}</h2>
        </div>
        <button
          onClick={onClose}
          className="p-1 text-gray-400 hover:text-gray-600 hover:bg-gray-200 rounded transition-colors"
          aria-label="Close preview"
        >
          <X className="w-5 h-5" />
        </button>
      </div>

      <div className="flex-1 flex overflow-hidden">
        <div className="w-64 border-r border-gray-200 bg-gray-50 p-3 overflow-y-auto scrollbar-thin flex-shrink-0">
          <div className="mb-4">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="搜索文档..."
                className="w-full pl-9 pr-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500/20 focus:border-primary-400"
              />
            </div>
          </div>
          
          {searchQuery ? (
            <div className="space-y-2">
              <p className="text-xs text-gray-500 font-medium mb-2">高亮搜索结果</p>
              <button
                onClick={handleContentClick}
                className="w-full flex items-center gap-2 px-3 py-2 text-sm text-primary-600 hover:bg-primary-50 rounded-lg transition-colors"
              >
                <Highlighter className="w-4 h-4" />
                <span>高亮显示: "{searchQuery}"</span>
              </button>
            </div>
          ) : (
            <div className="space-y-1">
              <p className="text-xs text-gray-500 font-medium mb-2">文档大纲</p>
              {sections.length > 0 ? (
                sections.map((section) => (
                  <button
                    key={section.id}
                    onClick={() => scrollToSection(section.id)}
                    className={`w-full flex items-center gap-2 px-3 py-2 text-sm rounded-lg transition-colors text-left ${
                      activeSection === section.id
                        ? 'bg-primary-100 text-primary-700 font-medium'
                        : 'text-gray-600 hover:bg-gray-100'
                    }`}
                    style={{ paddingLeft: `${(section.level - 1) * 12 + 12}px` }}
                  >
                    <ChevronRight className={`w-4 h-4 transition-transform flex-shrink-0 ${
                      activeSection === section.id ? 'rotate-90' : ''
                    }`} />
                    <span className="truncate">{section.title}</span>
                  </button>
                ))
              ) : (
                <p className="text-xs text-gray-400 px-3 py-2">暂无大纲</p>
              )}
            </div>
          )}
        </div>

        <div className="flex-1 overflow-y-auto p-6 scrollbar-thin">
          {searchQuery ? (
            <div
              className="markdown-content"
              dangerouslySetInnerHTML={{ __html: highlightContent }}
            />
          ) : (
            <div className="markdown-content">
              <ReactMarkdown
                remarkPlugins={[remarkGfm]}
                components={{
                  h1: ({ children, ...props }) => (
                    <h1 id={typeof children === 'string' ? children.toLowerCase().replace(/[^a-z0-9]+/g, '-') : ''} {...props}>
                      {children}
                    </h1>
                  ),
                  h2: ({ children, ...props }) => (
                    <h2 id={typeof children === 'string' ? children.toLowerCase().replace(/[^a-z0-9]+/g, '-') : ''} {...props}>
                      {children}
                    </h2>
                  ),
                  h3: ({ children, ...props }) => (
                    <h3 id={typeof children === 'string' ? children.toLowerCase().replace(/[^a-z0-9]+/g, '-') : ''} {...props}>
                      {children}
                    </h3>
                  ),
                }}
              >
                {content}
              </ReactMarkdown>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
