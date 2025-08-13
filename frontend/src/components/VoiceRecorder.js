import React from 'react';

const VoiceRecorder = ({ isRecording, currentText, error, onStop }) => {
  if (!isRecording && !error) return null;

  return (
    <div className="mb-4">
      {isRecording && (
        <div className="p-4 bg-gradient-to-r from-red-50 to-pink-50 border border-red-200 rounded-xl shadow-sm">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              {/* Animated microphone icon */}
              <div className="relative">
                <div className="w-10 h-10 bg-red-500 rounded-full flex items-center justify-center">
                  <span className="text-white text-lg">🎤</span>
                </div>
                {/* Pulsing ring animation */}
                <div className="absolute inset-0 w-10 h-10 border-2 border-red-400 rounded-full animate-ping"></div>
                <div className="absolute inset-0 w-10 h-10 border-2 border-red-300 rounded-full animate-pulse"></div>
              </div>
              
              <div className="flex-1">
                <div className="flex items-center gap-3">
                  <span className="text-sm font-medium text-red-700">Đang ghi âm...</span>
                  <div className="flex gap-1">
                    <div className="w-1 h-4 bg-red-500 rounded-full animate-bounce"></div>
                    <div className="w-1 h-4 bg-red-500 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                    <div className="w-1 h-4 bg-red-500 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                  </div>
                </div>
                
                {currentText && (
                  <div className="mt-2">
                    <span className="text-sm text-gray-700 bg-white px-3 py-2 rounded-lg border">
                      "{currentText}"
                    </span>
                    <div className="text-xs text-green-600 mt-1">
                      📝 Đang stream vào ô chat...
                    </div>
                  </div>
                )}
              </div>
            </div>
            
            <button
              onClick={onStop}
              className="px-4 py-2 bg-red-500 text-white text-sm rounded-lg hover:bg-red-600 transition-colors"
            >
              Dừng
            </button>
          </div>
        </div>
      )}
      
      {error && (
        <div className="p-4 bg-gradient-to-r from-yellow-50 to-orange-50 border border-yellow-200 rounded-xl">
          <div className="flex items-center gap-3">
            <span className="text-yellow-600 text-lg">⚠️</span>
            <span className="text-sm text-yellow-700">Lỗi: {error}</span>
          </div>
        </div>
      )}
    </div>
  );
};

export default VoiceRecorder;
