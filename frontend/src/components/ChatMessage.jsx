/**
 * ChatMessage Component
 * Displays individual chat messages
 */

import React from 'react';
import ReactMarkdown from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { oneDark } from 'react-syntax-highlighter/dist/esm/styles/prism';

const ChatMessage = ({ message, isUser }) => {
  const messageClass = isUser
    ? 'ml-auto mr-0 bg-blue-600 text-white rounded-lg rounded-br-none'
    : 'ml-0 mr-auto bg-gray-700 text-gray-100 rounded-lg rounded-bl-none';

  const containerClass = isUser ? 'flex justify-end' : 'flex justify-start';

  const timestamp = message.timestamp
    ? new Date(message.timestamp).toLocaleTimeString()
    : '';

  return (
    <div className={containerClass + ' mb-4'}>
      <div className={messageClass + ' max-w-xs md:max-w-md lg:max-w-lg px-4 py-3'}>
        <ReactMarkdown
          className="text-sm break-words prose prose-invert"
          components={{
            code({ node, inline, className, children, ...props }) {
              const match = /language-(\w+)/.exec(className || '');
              return !inline && match ? (
                <SyntaxHighlighter style={oneDark} language={match[1]} PreTag="div" {...props}>
                  {String(children).replace(/\n$/, '')}
                </SyntaxHighlighter>
              ) : (
                <code className={className + ' bg-gray-800 rounded px-1'} {...props}>
                  {children}
                </code>
              );
            }
          }}
        >
          {message.content || ''}
        </ReactMarkdown>

        {message.metadata && (
          <div className="text-xs opacity-70 mt-2">
            {message.metadata.tokens_used && (
              <span>Tokens: {message.metadata.tokens_used}</span>
            )}
            {message.metadata.model && (
              <span> · Model: {message.metadata.model}</span>
            )}
          </div>
        )}
        {timestamp && (
          <div className="text-xs opacity-50 mt-2">{timestamp}</div>
        )}
      </div>
    </div>
  );
};

export default ChatMessage;
