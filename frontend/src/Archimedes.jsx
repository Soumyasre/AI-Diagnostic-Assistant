import { useState , useEffect} from "react";
import ChatbotIcon from "./components/ChatBotIcon";
import ChatForm from "./components/ChatForm";
import ChatMessage from "./components/ChatMessage";
import { info } from "./components/python";
import { useLocation } from "react-router-dom";

const Archimedes = () => {
  const [chatHistory, setChatHistory] = useState([{
    hideInChat:true,
    role:"model",
    text: info
  },]);
  const location = useLocation();
  const user_id = location.state?.user_id;
  const backendUrl = 'http://127.0.0.1:5000'; // Replace with your backend URL

    useEffect(() => {
        const fetchChatHistory = async () => {
            try {
                const response = await fetch(`${backendUrl}/history/${user_id}`);
                if (!response.ok) {
                    console.error(`Failed to fetch chat history: ${response.status}`);
                    setChatHistory([{
                        hideInChat: true,
                        role: "model",
                        text: "Failed to load previous chat history.",
                    }]);
                    return;
                }
                const data = await response.json();
                // Format the history from the backend to match your chatHistory structure
                const formattedHistory = data.map(item => ({
                    role: item.role,
                    text: item.text,
                }));
                setChatHistory(formattedHistory);
            } catch (error) {
                console.error('Error fetching chat history:', error);
                setChatHistory([{
                    hideInChat: true,
                    role: "model",
                    text: "Error loading previous chat history.",
                }]);
            }
        };

        fetchChatHistory();
    }, [backendUrl, user_id]);

  // ✅ Mark function as async
  const generateBotResponse = async (history, message) => {
    console.log("User message sent:", message);
    const updateHistory = (text) => {
        setChatHistory(prev => [...prev.filter(msg => msg.text !== "Thinking..."), { role: "model", text }]);
    };

    // If your backend manages history, you might not need to send the entire history
    // history = history.map(({ role, text }) => ({ role, parts: [{ text }] }));

    try {
        const response = await fetch('http://127.0.0.1:5000/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message: message, user_id: user_id }),
        });

        const data = await response.json();

        if (!response.ok) {
            let errorMessage = "Something went wrong!";
            if (data && data.error) {
                errorMessage = data.error; // Assuming your backend sends an "error" key for errors
            }
            throw new Error(errorMessage);
        }

        const apiResponseText = data.response; // Access the bot's response from the "response" key
        updateHistory(apiResponseText.replace(/\*\*(.*?)\*\*/g, "$1").trim()); // Apply markdown cleanup if needed

        console.log("Backend response:", data);

    } catch (error) {
        console.error("Error communicating with backend:", error);
        updateHistory("Error: Could not get response from the bot."); // Update UI with an error message
    }
};

  return (
    <div className="Container">
      <div className="chatbot-popup">
        <div className="chat-header">
          <div className="header-info">
            {/* <button className = "delete" onClick={setChatHistory([])}>Reset</button> */}
            <ChatbotIcon />
            <h2 className="logo-Text"><i>SamaVeda</i></h2>
          </div>
        </div>

        {/* ✅ Chat Body */}
        <div className="chat-body">
          <div className="message bot-message">
            <ChatbotIcon />
            <p className="message-text">Hello {user_id} , how can I help you?</p>
          </div>

          {/* ✅ Render messages correctly */}
          {chatHistory.map((chat, index) => (
            <ChatMessage key={index} chat={chat} />
          ))}
  
        </div>

        {/* ✅ Chat Footer */}
        <div className="chat-footer">
          <ChatForm chatHistory={chatHistory} setChatHistory={setChatHistory} generateBotResponse={generateBotResponse} />
        </div>
      </div>
    </div>
    
  );
};

export default Archimedes;
