import React, { useRef, useEffect } from 'react';

function MessageInput({ inputMessage, setInputMessage, handleKeyPress, onSend, isLoading, onVoiceInput, isVoiceStreaming }) {
  const textareaRef = useRef(null);

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = Math.min(textareaRef.current.scrollHeight, 120) + 'px'; // tối đa ~5 dòng
    }
  }, [inputMessage]);

  // Sử dụng onKeyDown để phân biệt Enter và Shift+Enter
  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      onSend();
    }
  };

  return (
    <div className="flex gap-3 items-end">
      <div className="flex-1 relative">
        <textarea
          ref={textareaRef}
          value={inputMessage}
          onChange={(e) => setInputMessage(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Nhập câu hỏi của bạn... (Shift + Enter để xuống dòng)"
          className={`w-full px-4 py-3 border border-gray-300 rounded-xl text-sm outline-none transition-colors focus:border-blue-500 resize-none ${
            isVoiceStreaming ? 'border-green-400 bg-green-50' : ''
          }`}
          disabled={isLoading}
          rows={1}
          style={{ minHeight: '48px', maxHeight: '120px' }}
        />
        {/* Voice streaming indicator */}
        {isVoiceStreaming && (
          <div className="absolute right-3 bottom-3">
            <div className="flex space-x-1">
              <div className="w-1 h-3 bg-green-500 rounded-full animate-bounce"></div>
              <div className="w-1 h-3 bg-green-500 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
              <div className="w-1 h-3 bg-green-500 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
            </div>
          </div>
        )}
      </div>
      
      {/* Voice Input Button */}
      <button
        onClick={onVoiceInput}
        disabled={isLoading}
        className={`border-none w-12 h-12 rounded-xl cursor-pointer flex items-center justify-center text-lg disabled:opacity-50 disabled:cursor-not-allowed transition-all ${
          isVoiceStreaming 
            ? 'bg-green-500 text-white animate-pulse' 
            : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
        }`}
        title="Nhập bằng giọng nói"
      >
        🎤
      </button>
      
      <button
        onClick={onSend}
        disabled={!inputMessage.trim() || isLoading}
        className="bg-blue-600 text-white border-none w-12 h-12 rounded-xl cursor-pointer flex items-center justify-center text-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-blue-700 transition-colors"
        title="Gửi tin nhắn"
      >
        ➤
      </button>
    </div>
  );
}

export default MessageInput; 