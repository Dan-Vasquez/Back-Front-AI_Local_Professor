import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

const Message = ({ message }) => {
  const isUser = message.role === 'user';
  
  return (
    <div className={`message ${isUser ? 'user-message' : 'assistant-message'}`}>
      <div className="message-header">
        <strong>{isUser ? 'Tú' : 'Profesor de inglés'}</strong>
      </div>
      <div className="message-content markdown-content">
        <ReactMarkdown 
          remarkPlugins={[remarkGfm]}
          components={{
            // Personalización de elementos de markdown si es necesario
            h1: ({node, ...props}) => <h1 className="md-heading" {...props} />,
            h2: ({node, ...props}) => <h2 className="md-heading" {...props} />,
            h3: ({node, ...props}) => <h3 className="md-heading" {...props} />,
            p: ({node, ...props}) => <p className="md-paragraph" {...props} />,
            ul: ({node, ...props}) => <ul className="md-list" {...props} />,
            ol: ({node, ...props}) => <ol className="md-list" {...props} />,
            li: ({node, ...props}) => <li className="md-list-item" {...props} />,
            code: ({node, inline, ...props}) => 
              inline 
                ? <code className="md-inline-code" {...props} />
                : <pre className="md-code-block"><code {...props} /></pre>,
          }}
        >
          {message.content}
        </ReactMarkdown>
      </div>
    </div>
  );
};

export default Message;