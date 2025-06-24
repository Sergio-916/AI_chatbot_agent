import { useState } from "react";
import styles from "./AiChatbot.module.css";
import ReactMarkdown from "react-markdown";

function AiChatbot() {
  const [userInput, setUserInput] = useState<string>("");
  const [messages, setMessages] = useState("");
  const [processTime, setProcessTime] = useState(0);
  const [isLoading, setIsLoading] = useState<boolean>(false); // New state for loading spinner
  const [query, setQuery] = useState("");

  const backendUrl = import.meta.env.VITE_BACKEND_URL;

  const handleKeyDown = (event: React.KeyboardEvent<HTMLInputElement>) => {
    if (event.key === "Enter" && userInput.trim() !== "") {
      event.preventDefault();
      handleSendMessage();
    }
  };

  const handleSendMessage = async () => {
    if (userInput.trim() === "") return;
    setIsLoading(true); // Start loading
    setMessages("");
    setQuery(userInput);

    try {
      const responseData = await sendMessage(userInput);
      setMessages(responseData.message);
      setProcessTime(responseData.process_time);
      setUserInput("");
    } catch (e) {
      console.error("Error sending from component:", e);
    } finally {
      setIsLoading(false); // End loading regardless of success or failure
    }
  };

  const sendMessage = async (payload: string) => {
    const res = await fetch(`${backendUrl}/ai`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ message: payload }),
    });

    if (!res.ok) {
      const errorData = await res
        .json()
        .catch(() => ({ detail: res.statusText }));
      throw new Error(
        `Error HTTP: ${res.status} - ${errorData.detail || res.statusText}`
      );
    }
    return res.json();
  };

  return (
    <div className={styles.container}>
      <h2 className={styles.title}>BA Schools Chatbot</h2>
      <div className={styles.inputContainer}>
        <input
          type="text"
          placeholder="Enter your question..."
          value={userInput}
          onChange={(event) => setUserInput(event.target.value)}
          onKeyDown={handleKeyDown}
          disabled={isLoading} // Disable input while loading
          className={styles.inputField}
        />
        <button
          onClick={handleSendMessage}
          disabled={userInput.trim() === "" || isLoading} // Disable button while loading or input is empty
          className={styles.sendButton}
        >
          Send
        </button>
      </div>
      <hr className={styles.separator} /> {/* Styled separator */}
      {/* Message area */}
      {messages && <div className={styles.question}>Question: {query}</div>}
      <div className={styles.messageArea}>
        {" "}
        {/* Message area */}
        {isLoading ? (
          <div className={styles.loadingSpinner}>Loading...</div> // Simple loading spinner
        ) : messages ? (
          <>
            <div className={`${styles.message} ${styles.answer}`}>
              <ReactMarkdown>{`**Response:** ${messages}`}</ReactMarkdown>
            </div>
            {processTime > 0 && (
              <div className={styles.processTime}>
                Processing time: {processTime.toFixed(2)} sec.
              </div>
            )}
          </>
        ) : (
          userInput.trim() !== "" && ( // Show the question only when userInput is not empty and there is no answer
            <div className={`${styles.message} ${styles.question}`}>
              **Question:** {userInput}
            </div>
          )
        )}
      </div>
      <div className={styles.author}>Created by @ Sergey Shpak</div>
    </div>
  );
}

export default AiChatbot;
