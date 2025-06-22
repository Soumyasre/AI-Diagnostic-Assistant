import { useRef } from "react";

const  ChatForm=({chatHistory, setChatHistory, generateBotResponse})=>{
    const inputRef=useRef();

    const handleFormSubmit=(e)=>{
        e.preventDefault();
        console.log("oye");
        const userMessage=inputRef.current.value.trim();
        if(!userMessage) return;
        inputRef.current.value= "";

        setChatHistory((history)=>[...history, {role:"user",text: userMessage}]);

        setTimeout(()=> {
            setChatHistory((history)=>[...history, {role:"model",text: "Thinking..."}]);
         
        generateBotResponse(chatHistory, userMessage);},600);
    };




    return (
        <form action = "#" className="chat-form" onSubmit={handleFormSubmit}>
          <input ref={inputRef} type = "text" placeholder="Message..."
          className="message-input" required />
          <button className="material-symbols-outlined">keyboard_double_arrow_up</button>
          {/* <button className="material-symbols-outlined" onClick={setChatHistory([])}>keyboard_double_arrow_up</button> */}
        </form>

    );
};

export default ChatForm;

