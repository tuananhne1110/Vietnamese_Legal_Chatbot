import React from 'react';
import ReactMarkdown from 'react-markdown';

function Message({ message, showSources, toggleSources }) {
  return (
    <div className={`mb-6 ${message.type === 'user' ? 'flex justify-end' : 'flex justify-start'}`}>
      <div className={`max-w-3xl px-6 py-4 rounded-2xl ${
        message.type === 'user'
          ? 'bg-blue-600 text-white'
          : message.type === 'error'
          ? 'bg-red-100 text-red-800 border border-red-200'
          : 'bg-gray-100 text-gray-900'
      }`}>
        <div className="flex items-start gap-3">
          {/* Avatar */}
          <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-semibold flex-shrink-0 ${
            message.type === 'user'
              ? 'bg-blue-700 text-white'
              : 'bg-gray-200 text-gray-600'
          }`}>
            {message.type === 'user' ? '👤' : '🤖'}
          </div>
          
          <div className="flex-1 min-w-0">
            {/* Message content */}
            <div className="prose prose-sm max-w-none">
              {/* Loại bỏ hoặc thay thế link file trong nội dung trả lời */}
              {(() => {
                const fileUrlRegex = /https?:\/\/\S+\.(docx?|pdf|xlsx?|zip|rar)(\?\S*)?/gi;
                // Thay thế link file bằng thông báo ngắn gọn
                const contentWithoutLinks = message.content.replace(fileUrlRegex, '[📥 Tải về mẫu ở phía dưới]');
                return <ReactMarkdown>{contentWithoutLinks}</ReactMarkdown>;
              })()}
            </div>
            
            {/* File download button */}
            {message.sources && message.sources.length > 0 && (() => {
              // Chỉ lấy file đầu tiên có file_url hợp lệ
              const firstDownloadable = message.sources.find(
                source => (source.file_url || source.url || '').match(/\.(docx?|pdf|xlsx?|zip|rar)(\?.*)?$/i)
              );
              if (firstDownloadable) {
                const fileUrl = firstDownloadable.file_url || firstDownloadable.url;
                const fileName =
                  firstDownloadable.code
                    ? `mau_${firstDownloadable.code}.docx`
                    : firstDownloadable.title
                    ? firstDownloadable.title.replace(/\s+/g, '_') + '.docx'
                    : fileUrl.split('/').pop()?.split('?')[0] || 'downloaded_file';
                return (
                  <div className="mt-3">
                    <a
                      href={fileUrl}
                      download={fileName}
                      target="_blank"
                      rel="noopener noreferrer"
                      className={`inline-flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                        message.type === 'user'
                          ? 'bg-blue-700 text-white hover:bg-blue-800'
                          : 'bg-white text-blue-600 hover:bg-gray-50 border border-gray-200'
                      }`}
                    >
                      <span>📥</span>
                      <span>Tải về {firstDownloadable.code ? `mẫu ${firstDownloadable.code}` : fileName}</span>
                    </a>
                  </div>
                );
              }
              return null;
            })()}
            
            {/* Sources */}
            {message.sources && message.sources.length > 0 && (
              <div className="mt-3">
                <button
                  onClick={() => toggleSources(message.id)}
                  className={`text-sm flex items-center gap-2 transition-colors ${
                    message.type === 'user'
                      ? 'text-blue-200 hover:text-white'
                      : 'text-gray-600 hover:text-gray-800'
                  }`}
                >
                  <span>📖</span>
                  <span>
                    {showSources[message.id] ? 'Ẩn' : 'Hiện'} nguồn ({message.sources.length})
                  </span>
                </button>
                
                {showSources[message.id] && (
                  <div className="mt-3 space-y-2">
                    {message.sources.map((source, index) => (
                      <div key={index} className={`p-3 rounded-lg text-sm ${
                        message.type === 'user'
                          ? 'bg-blue-700 text-blue-100'
                          : 'bg-white border border-gray-200'
                      }`}>
                        {/* Nếu là nguồn luật */}
                        {source.law_name && (
                          <>
                            <div className="font-medium mb-1">{source.law_name}</div>
                            {source.article && <div className="text-xs opacity-80">Điều: {source.article}</div>}
                            {source.chapter && <div className="text-xs opacity-80">Chương: {source.chapter}</div>}
                            {source.clause && <div className="text-xs opacity-80">Khoản: {source.clause}</div>}
                            {source.point && <div className="text-xs opacity-80">Điểm: {source.point}</div>}
                          </>
                        )}
                        {/* Nếu là nguồn biểu mẫu */}
                        {source.title && (
                          <>
                            <div className="font-medium mb-1">
                              {source.title} {source.code && <span className="text-xs opacity-80">({source.code})</span>}
                            </div>
                            {source.file_url && (
                              <a
                                href={source.file_url}
                                download={source.code ? `mau_${source.code}.docx` : undefined}
                                target="_blank"
                                rel="noopener noreferrer"
                                className={`text-xs underline ${
                                  message.type === 'user' ? 'text-blue-200' : 'text-blue-600'
                                }`}
                              >
                                📥 Tải về
                              </a>
                            )}
                          </>
                        )}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}
            
            {/* Timestamp */}
            <div className={`text-xs mt-2 ${
              message.type === 'user' ? 'text-blue-200' : 'text-gray-500'
            }`}>
              {new Date(message.timestamp).toLocaleTimeString('vi-VN', { 
                hour: '2-digit', 
                minute: '2-digit' 
              })}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Message; 