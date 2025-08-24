import React, { useState, useRef, useEffect } from 'react';
import Header from '../components/Header';
import ChatBubble from '../components/ChatBubble';
import MessageInput from '../components/MessageInput';
import { downloadPdf, getAnalytics, handleCommand } from '../api'; // Updated imports
import './ChatPage.css';
import Loader from '../components/Loader';

const ChatPage = () => {
  const [messages, setMessages] = useState([
    {
      sender: 'bot',
      text: "Hello! I'm your intelligent expense assistant. How can I help you today?",
    },
  ]);
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(scrollToBottom, [messages]);

  // ✅ SIMPLIFIED LOGIC
  const handleSendMessage = async (text) => {
    const newUserMessage = { sender: 'user', text };
    setMessages((prev) => [...prev, newUserMessage]);
    setIsLoading(true);

    try {
      // Send every text input to the single, smart /command endpoint
      const response = await handleCommand({ text });
      
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

  // Handler for the analytics button (no change)
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

  // Handler for the PDF download button (no change)
  const handleDownloadPdf = async () => {
    setIsLoading(true);
    try {
      await downloadPdf();
      const botMessage = {
        sender: 'bot',
        text: '✅ Your PDF report is downloading.',
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
      <MessageInput 
        onSend={handleSendMessage}
        onShowAnalytics={handleShowAnalytics}
        onDownloadPdf={handleDownloadPdf}
      />
    </div>
  );
};

export default ChatPage;