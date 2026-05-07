import { useState } from 'react';
import { ToastProvider, ToastContainer, useToast } from './components/Toast';
import { ChatHistory, ChatInput, type Message } from './components/Chat';
import { FileUpload } from './components/FileUpload';
import { DocumentPreview } from './components/DocumentPreview';
import { FileText, BookOpen, MessageSquare } from 'lucide-react';

function AppContent() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      content: '你好！我是你的AI助手。我可以帮你处理文档并回答相关问题。请先上传文档，然后随时向我提问。',
      isUser: false,
      timestamp: '刚刚',
    },
  ]);
  const [isLoading, setIsLoading] = useState(false);
  const [activeTab, setActiveTab] = useState<'chat' | 'upload'>('chat');
  const [previewDocument, setPreviewDocument] = useState<{ title: string; content: string } | null>(null);
  const toast = useToast();

  const handleSendMessage = async (content: string) => {
    setMessages((prev) => [
      ...prev,
      {
        id: `msg-${Date.now()}`,
        content,
        isUser: true,
        timestamp: '刚刚',
      },
    ]);

    setIsLoading(true);

    await new Promise((resolve) => setTimeout(resolve, 1500));

    const responses = [
      '这是一个很好的问题！让我来分析一下...\n\n根据文档内容，关键要点包括：\n\n1. **核心概念**：文档的主要观点\n2. **重要数据**：相关统计信息\n3. **建议行动**：下一步应该做什么',
      '感谢您的提问。基于文档内容，我为您整理了以下信息：\n\n- 关键点一\n- 关键点二\n- 关键点三\n\n如果您需要更详细的解释，请随时告诉我！',
      '好的，让我来回答您的问题。\n\n**答案摘要：**\n这是一个详细的回答，包含必要的上下文和参考信息。\n\n> 引用自文档内容\n\n希望这个回答能帮到您！',
    ];

    const randomResponse = responses[Math.floor(Math.random() * responses.length)];

    setMessages((prev) => [
      ...prev,
      {
        id: `msg-${Date.now()}-ai`,
        content: randomResponse,
        isUser: false,
        timestamp: '刚刚',
        source: {
          title: '参考文档',
        },
      },
    ]);

    setIsLoading(false);
  };

  const handleFilesUploaded = (files: File[]) => {
    toast.success(`成功上传 ${files.length} 个文件`);
    
    const firstFile = files[0];
    if (firstFile) {
      const reader = new FileReader();
      reader.onload = (e) => {
        const content = e.target?.result as string;
        setPreviewDocument({
          title: firstFile.name,
          content: content || '文档内容为空',
        });
      };
      reader.readAsText(firstFile);
    }
  };

  const sampleDocument = `# 文档标题

这是一个示例文档，用于演示文档预览功能。

## 章节一

这是第一节的内容。您可以在这里添加详细的描述文字。

### 子章节

支持三级标题嵌套，文档大纲会自动识别这些标题。

## 章节二

这是第二节的内容，包含一些列表：

- 列表项一
- 列表项二
- 列表项三

## 代码示例

\`\`\`javascript
function helloWorld() {
  console.log('Hello, World!');
}
\`\`\`

## 引用内容

> 这是一段引用文字，可以用来强调重要信息。

## 表格示例

| 功能 | 描述 | 状态 |
|------|------|------|
| 聊天 | 支持对话交互 | ✅ |
| 上传 | 支持文件上传 | ✅ |
| 预览 | 文档预览功能 | ✅ |

---

感谢您使用本系统！`;

  return (
    <div className="h-screen flex flex-col bg-gray-100">
      <header className="bg-white border-b border-gray-200 px-4 py-3">
        <div className="max-w-6xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-primary-500 to-primary-600 flex items-center justify-center">
              <FileText className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-lg font-semibold text-gray-800">AI 文档助手</h1>
              <p className="text-xs text-gray-500">智能问答与文档处理</p>
            </div>
          </div>
          
          <div className="flex items-center gap-1 bg-gray-100 rounded-lg p-1">
            <button
              onClick={() => setActiveTab('chat')}
              className={`flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                activeTab === 'chat'
                  ? 'bg-white text-primary-600 shadow-sm'
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              <MessageSquare className="w-4 h-4" />
              <span>聊天</span>
            </button>
            <button
              onClick={() => setActiveTab('upload')}
              className={`flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                activeTab === 'upload'
                  ? 'bg-white text-primary-600 shadow-sm'
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              <BookOpen className="w-4 h-4" />
              <span>文档上传</span>
            </button>
          </div>
        </div>
      </header>

      <main className="flex-1 flex overflow-hidden">
        {activeTab === 'chat' ? (
          <div className="flex-1 flex flex-col min-w-0">
            <ChatHistory messages={messages} isLoading={isLoading} />
            <ChatInput onSend={handleSendMessage} isLoading={isLoading} />
          </div>
        ) : (
          <div className="flex-1 p-6 overflow-auto">
            <div className="max-w-2xl mx-auto">
              <h2 className="text-xl font-semibold text-gray-800 mb-6">上传文档</h2>
              <FileUpload onFilesUploaded={handleFilesUploaded} />
              
              <div className="mt-6 p-4 bg-blue-50 rounded-xl border border-blue-100">
                <p className="text-sm text-blue-700">
                  💡 提示：上传文档后，您可以在聊天界面中提问，我会基于文档内容为您提供准确的回答。
                </p>
              </div>
            </div>
          </div>
        )}

        {previewDocument && (
          <div className="w-96 flex-shrink-0 border-l border-gray-200">
            <DocumentPreview
              title={previewDocument.title}
              content={previewDocument.content}
              onClose={() => setPreviewDocument(null)}
            />
          </div>
        )}

        {activeTab === 'upload' && !previewDocument && (
          <div className="w-96 flex-shrink-0 border-l border-gray-200 p-4">
            <DocumentPreview
              title="示例文档"
              content={sampleDocument}
              onClose={() => {}}
            />
          </div>
        )}
      </main>

      <ToastContainer />
    </div>
  );
}

export default function App() {
  return (
    <ToastProvider>
      <AppContent />
    </ToastProvider>
  );
}
