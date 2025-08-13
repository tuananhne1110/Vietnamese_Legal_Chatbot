import React, { useRef, useEffect, useState } from 'react';
import Message from './Message';
import MessageInput from './MessageInput';
import VoiceRecorder from './VoiceRecorder';
import VoiceTypingIndicator from './VoiceTypingIndicator';
import useVoiceToText from '../hooks/useVoiceToText';

function ChatInterface({ 
  messages, 
  onSend, 
  isLoading, 
  sessionId, 
  showSources, 
  toggleSources, 
  inputMessage, 
  setInputMessage, 
  handleKeyPress, 
  loadChatHistory, 
  clearChatHistory, 
  createNewSession,
  openCT01Modal
}) {
  const messagesEndRef = useRef(null);
  const [sidebarOpen, setSidebarOpen] = useState(false);

  // Voice-to-text hook
  const {
    isRecording,
    isLoading: voiceLoading,
    error: voiceError,
    currentText: voiceText,
    toggleRecording,
    stopRecording
  } = useVoiceToText((text) => {
    setInputMessage(text);
  });

  // Auto-send message when recording stops
  useEffect(() => {
    if (!isRecording && voiceText && voiceText.trim()) {
      // Small delay to ensure text is properly set
      const timer = setTimeout(() => {
        if (inputMessage && inputMessage.trim()) {
          onSend();
        }
      }, 300);
      
      return () => clearTimeout(timer);
    }
  }, [isRecording, voiceText, inputMessage, onSend]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleNewChat = () => {
    createNewSession();
    setSidebarOpen(false);
  };

  const handleClearHistory = () => {
    clearChatHistory();
    setSidebarOpen(false);
  };

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Sidebar */}
      <div className={`fixed inset-y-0 left-0 z-50 w-64 bg-white shadow-lg transform transition-transform duration-300 ease-in-out ${
        sidebarOpen ? 'translate-x-0' : '-translate-x-full'
      } lg:relative lg:translate-x-0`}>
        <div className="flex flex-col h-full">
          {/* Header */}
          <div className="flex items-center justify-between p-4 border-b">
            <h1 className="text-xl font-semibold text-gray-800">Trợ Lý Pháp Luật</h1>
            <button
              onClick={() => setSidebarOpen(false)}
              className="lg:hidden p-2 hover:bg-gray-100 rounded-lg"
            >
              <span className="text-xl">×</span>
            </button>
          </div>

          {/* New Chat Button */}
          <div className="p-4">
            <button
              onClick={handleNewChat}
              className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              <span>+</span>
              <span>Cuộc trò chuyện mới</span>
            </button>
          </div>

          {/* Chat History */}
          <div className="flex-1 overflow-y-auto p-4">
            <div className="space-y-2">
              <div className="text-sm font-medium text-gray-600 mb-2">Lịch sử trò chuyện</div>
              {messages.length > 0 ? (
                <div className="text-sm text-gray-500">
                  {messages.length} tin nhắn trong phiên này
                </div>
              ) : (
                <div className="text-sm text-gray-400 italic">
                  Chưa có lịch sử
                </div>
              )}
            </div>
          </div>

          {/* Footer */}
          <div className="p-4 border-t">
            <button
              onClick={handleClearHistory}
              className="w-full text-left px-3 py-2 text-sm text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
            >
              🗑️ Xóa lịch sử
            </button>
          </div>
        </div>
      </div>

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col">
        {/* Top Bar */}
        <div className="bg-white border-b px-4 py-3 flex items-center justify-between">
          <button
            onClick={() => setSidebarOpen(true)}
            className="lg:hidden p-2 hover:bg-gray-100 rounded-lg"
          >
            <span className="text-xl">☰</span>
          </button>
          <div className="flex items-center gap-3">
            <span className="text-lg font-semibold text-gray-800">Trợ Lý Pháp Luật Việt Nam</span>
            {sessionId && (
              <span className="text-xs text-gray-500 font-mono">
                {sessionId.substring(0, 8)}...
              </span>
            )}
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={openCT01Modal}
              className="px-3 py-1 bg-green-600 text-white text-sm rounded-lg hover:bg-green-700 transition-colors"
            >
              📝 CT01
            </button>
          </div>
        </div>

        {/* Messages Area */}
        <div className="flex-1 overflow-y-auto bg-white">
          {messages.length === 0 && !isLoading && (
            <div className="flex items-center justify-center h-full">
              <div className="text-center max-w-md mx-auto px-4">
                <div className="text-6xl mb-6">🤖</div>
                <h2 className="text-2xl font-semibold text-gray-800 mb-4">
                  Chào mừng đến với Trợ Lý Pháp Luật
                </h2>
                <p className="text-gray-600 mb-8">
                  Tôi là trợ lý AI chuyên về pháp luật Việt Nam. Hãy đặt câu hỏi để được hỗ trợ về các vấn đề pháp lý.
                </p>
                
                {/* Suggestion chips */}
                <div className="grid grid-cols-1 gap-3">
                  <button 
                    onClick={() => {
                      setInputMessage('Điền biểu mẫu CT01');
                      setTimeout(() => {
                        onSend();
                        openCT01Modal();
                      }, 100);
                    }}
                    className="text-left p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
                  >
                    <div className="flex items-center gap-3">
                      <span className="text-2xl">📝</span>
                      <div>
                        <div className="font-medium text-gray-800">Điền biểu mẫu CT01</div>
                        <div className="text-sm text-gray-600">Tờ khai thuế thu nhập cá nhân</div>
                      </div>
                    </div>
                  </button>
                  
                  <button 
                    onClick={() => setInputMessage('Tra cứu thủ tục hành chính')}
                    className="text-left p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
                  >
                    <div className="flex items-center gap-3">
                      <span className="text-2xl">🔍</span>
                      <div>
                        <div className="font-medium text-gray-800">Tra cứu thủ tục</div>
                        <div className="text-sm text-gray-600">Hướng dẫn thủ tục hành chính</div>
                      </div>
                    </div>
                  </button>
                  
                  <button 
                    onClick={() => setInputMessage('Tư vấn pháp luật')}
                    className="text-left p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
                  >
                    <div className="flex items-center gap-3">
                      <span className="text-2xl">⚖️</span>
                      <div>
                        <div className="font-medium text-gray-800">Tư vấn pháp luật</div>
                        <div className="text-sm text-gray-600">Hỏi đáp về các vấn đề pháp lý</div>
                      </div>
                    </div>
                  </button>
                </div>
              </div>
            </div>
          )}
          
          <div className="max-w-4xl mx-auto px-4 py-6">
            {messages.map((message) => (
              <Message 
                key={message.id} 
                message={message} 
                showSources={showSources} 
                toggleSources={toggleSources} 
              />
            ))}
            
            {/* Loading indicator */}
            {isLoading && (
              <div className="flex justify-start mb-6">
                <div className="bg-gray-100 rounded-lg p-4 max-w-2xl">
                  <div className="flex items-center gap-2">
                    <div className="w-6 h-6 bg-blue-600 rounded-full animate-pulse"></div>
                    <span className="text-gray-600">Đang trả lời...</span>
                  </div>
                </div>
              </div>
            )}
            
            <div ref={messagesEndRef} />
          </div>
        </div>

        {/* Voice Typing Indicator */}
        <VoiceTypingIndicator 
          isStreaming={isRecording && voiceText && voiceText.trim()} 
          text={voiceText} 
        />

        {/* Input Area */}
        <div className="bg-white border-t p-4">
          <div className="max-w-4xl mx-auto">
            <VoiceRecorder
              isRecording={isRecording}
              currentText={voiceText}
              error={voiceError}
              onStop={stopRecording}
            />
            
            <MessageInput
              inputMessage={inputMessage}
              setInputMessage={setInputMessage}
              handleKeyPress={handleKeyPress}
              onSend={onSend}
              isLoading={isLoading || voiceLoading}
              onVoiceInput={toggleRecording}
              isVoiceStreaming={isRecording && voiceText && voiceText.trim()}
            />
          </div>
        </div>
      </div>

      {/* Overlay for mobile sidebar */}
      {sidebarOpen && (
        <div 
          className="fixed inset-0 bg-black bg-opacity-50 z-40 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}
    </div>
  );
}

export default ChatInterface;
