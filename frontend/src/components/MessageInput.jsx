// import React, { useState } from 'react';
// import { FiSend } from 'react-icons/fi';
// import './MessageInput.css';

// const MessageInput = ({ onSend }) => {
//   const [text, setText] = useState('');

//   const handleSend = () => {
//     if (text.trim()) {
//       onSend(text);
//       setText('');
//     }
//   };

//   const handleKeyPress = (e) => {
//     if (e.key === 'Enter') {
//       handleSend();
//     }
//   };

//   return (
//     <div className="message-input-container">
//       <input
//         type="text"
//         value={text}
//         onChange={(e) => setText(e.target.value)}
//         onKeyPress={handleKeyPress}
//         placeholder="Type your expense or question..."
//       />
//       <button onClick={handleSend}><FiSend size={20} /></button>
//     </div>
//   );
// };

// export default MessageInput;



import React, { useState } from 'react';
import { FiSend, FiPieChart, FiDownload } from 'react-icons/fi'; // ✅ Import new icons
import './MessageInput.css';

// ✅ Add new props: onShowAnalytics, onDownloadPdf
const MessageInput = ({ onSend, onShowAnalytics, onDownloadPdf }) => { 
  const [text, setText] = useState('');

  const handleSend = () => {
    if (text.trim()) {
      onSend(text);
      setText('');
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleSend();
    }
  };

  return (
    <div className="message-input-container">
      {/* ✅ New Buttons */}
      <button onClick={onShowAnalytics} className="action-button" title="Show Analytics">
        <FiPieChart size={20} />
      </button>
      <button onClick={onDownloadPdf} className="action-button" title="Download PDF Report">
        <FiDownload size={20} />
      </button>
      
      <input
        type="text"
        value={text}
        onChange={(e) => setText(e.target.value)}
        onKeyPress={handleKeyPress}
        placeholder="Type your expense or question..."
      />
      <button onClick={handleSend} className="send-button"><FiSend size={20} /></button>
    </div>
  );
};

export default MessageInput;