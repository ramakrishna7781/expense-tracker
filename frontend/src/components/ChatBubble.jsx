// import React from 'react';
// import './ChatBubble.css';
// import BotIcon from '../assets/chat-icon.svg';

// const formatBotResponse = (data) => {
//     if (typeof data === 'string' || !data) {
//         return <p>{data || 'Sorry, I did not understand that.'}</p>;
//     }
    
//     // Default message
//     let content = <p>{data.message || data.response}</p>;

//     // Custom rendering for list expenses
//     if (data.expenses) {
//         content = (
//             <div>
//                 <p><strong>Total Expenses:</strong> {data.total_expenses}</p>
//                 {data.summary && Object.keys(data.summary).length > 0 && (
//                     <>
//                         <strong>Summary:</strong>
//                         <ul>{Object.entries(data.summary).map(([cat, total]) => <li key={cat}>{cat}: Rs.{total.toFixed(2)}</li>)}</ul>
//                     </>
//                 )}
//                 {data.expenses.map(exp => (
//                     <div key={exp._id} className="expense-item-card">
//                        <p><strong>{exp.description}</strong></p>
//                        <p>Amount: Rs.{exp.amount} | Category: {exp.category}</p>
//                     </div>
//                 ))}
//             </div>
//         );
//     }
//     // Custom rendering for suggestions
//     else if (data.remaining_budget !== undefined) {
//         content = (
//             <div>
//                 <p>{data.message}</p>
//                 <strong>Budget Details:</strong>
//                 <ul>
//                     <li>Salary: Rs.{data.salary}</li>
//                     <li>Total Spent: Rs.{data.total_spent}</li>
//                     <li style={{fontWeight: 'bold'}}>Remaining: Rs.{data.remaining_budget}</li>
//                 </ul>
//             </div>
//         );
//     }

//     return content;
// };

// const ChatBubble = ({ message }) => {
//   const isUser = message.sender === 'user';
//   return (
//     <div className={`bubble-container ${isUser ? 'user' : 'bot'}`}>
//       {!isUser && <img src={BotIcon} alt="bot" className="bot-avatar"/>}
//       <div className="bubble">
//         {message.text ? <p>{message.text}</p> : formatBotResponse(message.data)}
//       </div>
//     </div>
//   );
// };

// export default ChatBubble;



import React from 'react';
import './ChatBubble.css';
import BotIcon from '../assets/chat-icon.svg';
import AnalyticsDisplay from './AnalyticsDisplay'; // ✅ Import the new component

const formatBotResponse = (data) => {
    if (typeof data === 'string' || !data) {
        return <p>{data || 'Sorry, I did not understand that.'}</p>;
    }
    
    // ✅ Custom rendering for Analytics
    if (data.analytics) {
        return <AnalyticsDisplay analyticsData={data.analytics} />;
    }

    // Default message
    let content = <p>{data.message || data.response}</p>;

    // Custom rendering for list expenses
    // if (data.expenses) {
    //     content = (
    //         <div>
    //             <p><strong>Total Expenses:</strong> {data.total_expenses}</p>
    //             {data.summary && Object.keys(data.summary).length > 0 && (
    //                 <>
    //                     <strong>Summary:</strong>
    //                     <ul>{Object.entries(data.summary).map(([cat, total]) => <li key={cat}>{cat}: Rs.{total.toFixed(2)}</li>)}</ul>
    //                 </>
    //             )}
    //             {data.expenses.map(exp => (
    //                 <div key={exp._id} className="expense-item-card">
    //                    <p><strong>{exp.description}</strong></p>
    //                    <p>Amount: Rs.{exp.amount} | Category: {exp.category}</p>
    //                 </div>
    //             ))}
    //         </div>
    //     );
    // }

    if (data.analytics) {
        return <AnalyticsDisplay analyticsData={data.analytics} />;
    }
    
    // ✅ ADD THIS BLOCK to handle the confirmation message after adding an expense.
    if (data.status === 'success' && data.expense) {
        const { expense } = data;
        return (
            <div>
                <p><strong>✅ Expense Added!</strong></p>
                <div className="expense-item-card">
                    <p><strong>Description:</strong> {expense.description}</p>
                    <p><strong>Amount:</strong> Rs.{expense.amount.toFixed(2)}</p>
                    <p><strong>Category:</strong> {expense.category}</p>
                </div>
            </div>
        );
    }
    // Custom rendering for suggestions
    else if (data.remaining_budget !== undefined) {
        content = (
            <div>
                <p>{data.message}</p>
                <strong>Budget Details:</strong>
                <ul>
                    <li>Salary: Rs.{data.salary}</li>
                    <li>Total Spent: Rs.{data.total_spent}</li>
                    <li style={{fontWeight: 'bold'}}>Remaining: Rs.{data.remaining_budget}</li>
                </ul>
            </div>
        );
    }

    return content;
};

const ChatBubble = ({ message }) => {
  const isUser = message.sender === 'user';
  return (
    <div className={`bubble-container ${isUser ? 'user' : 'bot'}`}>
      {!isUser && <img src={BotIcon} alt="bot" className="bot-avatar"/>}
      <div className="bubble">
        {message.text ? <p>{message.text}</p> : formatBotResponse(message.data)}
      </div>
    </div>
  );
};

export default ChatBubble;