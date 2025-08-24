// import React, { useState, useRef, useEffect } from 'react';
// import Header from '../components/Header';
// import ChatBubble from '../components/ChatBubble';
// import MessageInput from '../components/MessageInput';
// import { addExpense, listExpenses, suggestSpending, setSalary, downloadPdf } from '../api';
// import './ChatPage.css';
// import Loader from '../components/Loader';

// const ChatPage = () => {
//   const [messages, setMessages] = useState([
//     {
//       sender: 'bot',
//       text: "Hello! How can I help you track your expenses today? You can say things like:\n- 'Spent 500 on food'\n- 'Show my expenses for this month'\n- 'Can I spend 200 today?'\n- 'Set my salary to 50k'",
//     },
//   ]);
//   const [isLoading, setIsLoading] = useState(false);
//   const messagesEndRef = useRef(null);

//   const scrollToBottom = () => {
//     messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
//   };

//   useEffect(scrollToBottom, [messages]);

//   const handleSendMessage = async (text) => {
//     const newUserMessage = { sender: 'user', text };
//     setMessages((prev) => [...prev, newUserMessage]);
//     setIsLoading(true);

//     try {
//       const lowerCaseText = text.toLowerCase();
//       let response;

//       // Simple routing based on keywords
//       if (lowerCaseText.startsWith('add ') || lowerCaseText.startsWith('spent ') || /^\d/.test(lowerCaseText)) {
//         response = await addExpense({ text });
//       } else if (lowerCaseText.includes('list') || lowerCaseText.includes('show')) {
//         response = await listExpenses(text);
//       } else if (lowerCaseText.includes('salary')) {
//         const salary = text.match(/\d+k?/i)?.[0];
//         response = await setSalary(salary);
//       } else if (lowerCaseText.includes('download') || lowerCaseText.includes('report')) {
//         await downloadPdf();
//         response = { data: { message: "Your PDF report is downloading." } };
//       } else {
//         response = await suggestSpending(text);
//       }
      
//       const botMessage = { sender: 'bot', data: response.data };
//       setMessages((prev) => [...prev, botMessage]);
//     } catch (error) {
//       const errorMessage = {
//         sender: 'bot',
//         text: `Sorry, an error occurred: ${error.response?.data?.detail || error.message}`,
//       };
//       setMessages((prev) => [...prev, errorMessage]);
//     } finally {
//       setIsLoading(false);
//     }
//   };

//   return (
//     <div className="chat-page">
//       <Header />
//       <div className="chat-area">
//         {messages.map((msg, index) => (
//           <ChatBubble key={index} message={msg} />
//         ))}
//         {isLoading && (
//           <div className="loader-container">
//             <Loader />
//           </div>
//         )}
//         <div ref={messagesEndRef} />
//       </div>
//       <MessageInput onSend={handleSendMessage} />
//     </div>
//   );
// };

// export default ChatPage;


import React, { useState, useRef, useEffect } from 'react';
import Header from '../components/Header';
import ChatBubble from '../components/ChatBubble';
import MessageInput from '../components/MessageInput';
// ✅ Import getAnalytics
import { addExpense, listExpenses, suggestSpending, setSalary, downloadPdf, getAnalytics } from '../api';
import './ChatPage.css';
import Loader from '../components/Loader';

const ChatPage = () => {
  const [messages, setMessages] = useState([
    {
      sender: 'bot',
      text: "Hello! How can I help you track your expenses today? You can say things like:\n- 'Spent 500 on food'\n- 'Show my expenses for this month'\n- 'Can I spend 200 today?'\n- 'Set my salary to 50k'",
    },
  ]);
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(scrollToBottom, [messages]);

  const handleSendMessage = async (text) => {
    const newUserMessage = { sender: 'user', text };
    setMessages((prev) => [...prev, newUserMessage]);
    setIsLoading(true);

    try {
      const lowerCaseText = text.toLowerCase();
      let response;

      // Simple routing based on keywords
      if (lowerCaseText.startsWith('add ') || lowerCaseText.startsWith('spent ') || /^\d/.test(lowerCaseText)) {
        response = await addExpense({ text });
      } else if (lowerCaseText.includes('list') || lowerCaseText.includes('show')) {
        response = await listExpenses(text);
      } else if (lowerCaseText.includes('salary')) {
        const salary = text.match(/\d+k?/i)?.[0];
        response = await setSalary(salary);
      } else if (lowerCaseText.includes('download') || lowerCaseText.includes('report')) {
        await downloadPdf();
        response = { data: { message: "Your PDF report is downloading." } };
      } else {
        response = await suggestSpending(text);
      }
      
      const botMessage = { sender: 'bot', data: response.data };
      setMessages((prev) => [...prev, botMessage]);
    } catch (error) {
      const errorMessage = {
        sender: 'bot',
        text: `Sorry, an error occurred: ${error.response?.data?.detail || error.message}`,
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  // ✅ New handler for the analytics button
  const handleShowAnalytics = async () => {
    setIsLoading(true);
    try {
      const response = await getAnalytics();
      const botMessage = { sender: 'bot', data: response.data };
      setMessages((prev) => [...prev, botMessage]);
    } catch (error) {
      const errorMessage = {
        sender: 'bot',
        text: `Could not fetch analytics: ${error.response?.data?.detail || error.message}`,
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  // ✅ New handler for the PDF download button
  const handleDownloadPdf = async () => {
    setIsLoading(true);
    try {
      await downloadPdf();
      const botMessage = {
        sender: 'bot',
        text: '✅ Your PDF report for the last month is downloading.',
      };
      setMessages((prev) => [...prev, botMessage]);
    } catch (error) {
      const errorMessage = {
        sender: 'bot',
        text: `Could not download PDF: ${error.response?.data?.detail || error.message}`,
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="chat-page">
      <Header />
      <div className="chat-area">
        {messages.map((msg, index) => (
          <ChatBubble key={index} message={msg} />
        ))}
        {isLoading && (
          <div className="loader-container">
            <Loader />
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>
      {/* ✅ Pass the new handlers as props */}
      <MessageInput 
        onSend={handleSendMessage}
        onShowAnalytics={handleShowAnalytics}
        onDownloadPdf={handleDownloadPdf}
      />
    </div>
  );
};

export default ChatPage;