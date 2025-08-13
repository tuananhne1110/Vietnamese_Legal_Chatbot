import React from 'react';

const VoiceTypingIndicator = ({ isStreaming, text }) => {
  if (!isStreaming || !text) return null;

  return (
    <div className="flex items-center gap-3 text-sm text-green-600 bg-green-50 px-4 py-3 rounded-xl border border-green-200 mx-4 mb-4">
      <div className="flex space-x-1">
        <div className="w-1 h-4 bg-green-500 rounded-full animate-bounce"></div>
        <div className="w-1 h-4 bg-green-500 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
        <div className="w-1 h-4 bg-green-500 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
      </div>
      <span>🎤 Đang ghi âm...</span>
      <span className="text-gray-700">"{text}"</span>
    </div>
  );
};

export default VoiceTypingIndicator;
