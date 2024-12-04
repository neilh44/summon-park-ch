import React, { useState, useRef, useEffect } from "react";
import { Mountain, Image, MoreVertical, Share2, Camera, Video, Paperclip } from 'lucide-react';
import "tailwindcss/tailwind.css";
import DataVisualization from "../../bu_src/src/components/datavisualization";

// Interface for Chat Messages
interface ChatMessage {
  id: number;
  type: 'user' | 'system';
  content: string;
  responseData?: BackendResponse | null;
}

// Interface for Backend Response
interface BackendResponse {
  query_results?: number[][];
  nl_explanation?: string;
  error?: string;
}

const JourneyUI: React.FC = () => {
  // State Hooks
  const [userInput, setUserInput] = useState<string>("");
  const [responseData, setResponseData] = useState<BackendResponse | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [activeTab, setActiveTab] = useState<string>("book");
  const [isSidebarOpen, setIsSidebarOpen] = useState<boolean>(false);
  const [chatHistory, setChatHistory] = useState<ChatMessage[]>([]);

  // Ref for chat messages container
  const chatContainerRef = useRef<HTMLDivElement>(null);

  // Backend API URL
  const BACKEND_URL = "http://127.0.0.1:5000/query";

  // Scroll to bottom of chat when messages change
  useEffect(() => {
    if (chatContainerRef.current) {
      chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;
    }
  }, [chatHistory, isLoading]);

  // API Call Function
  const callBackendAPI = async (userInput: string) => {
    setIsLoading(true);
    
    // Add user message to chat history
    const userMessage: ChatMessage = {
      id: Date.now(),
      type: 'user',
      content: userInput
    };
    setChatHistory(prev => [...prev, userMessage]);

    try {
      const response = await fetch(BACKEND_URL, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ query: userInput }),
      });
  
      if (!response.ok) {
        throw new Error(`API request failed with status ${response.status}`);
      }
  
      const data: BackendResponse = await response.json();
      setResponseData(data);

      // Add system response to chat history
      if (data.nl_explanation) {
        const systemMessage: ChatMessage = {
          id: Date.now() + 1,
          type: 'system',
          content: data.nl_explanation,
          responseData: data
        };
        setChatHistory(prev => [...prev, systemMessage]);
      }
    } catch (error) {
      console.error("Error calling backend:", error);
      
      // Add error message to chat history
      const errorMessage: ChatMessage = {
        id: Date.now(),
        type: 'system',
        content: "An error occurred. Please try again."
      };
      setChatHistory(prev => [...prev, errorMessage]);
      
      setResponseData({ error: "An error occurred. Please try again." });
    } finally {
      setIsLoading(false);
    }
  };

  // Form Submit Handler
  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (userInput.trim()) {
      await callBackendAPI(userInput);
      setUserInput(""); // Clear input after submission
    }
  };

  // Toggle Sidebar
  const toggleSidebar = () => {
    setIsSidebarOpen(!isSidebarOpen);
  };

  return (
    <div className="flex h-screen flex-col bg-white">
      {/* Header */}
      <header className="flex flex-col sm:flex-row items-center justify-between border-b p-4 space-y-4 sm:space-y-0">
        <div className="flex flex-col sm:flex-row items-center gap-4 sm:gap-8 w-full sm:w-auto">
          <h1 className="text-xl font-semibold text-green-500">Summon Parking Valet</h1>
          <div className="flex border rounded-md w-full sm:w-auto">
            <button
              className={`flex-1 sm:flex-none px-4 py-2 ${activeTab === 'chat' ? 'bg-gray-100' : ''}`}
              onClick={() => setActiveTab('chat')}
            >
              Chat
            </button>
            <button
              className={`flex-1 sm:flex-none px-4 py-2 ${activeTab === 'book' ? 'bg-gray-100' : ''}`}
              onClick={() => setActiveTab('book')}
            >
              Visualization
            </button>
          </div>
        </div>
        <div className="flex items-center space-x-2">
          <button className="p-2 hover:bg-gray-100 rounded-full">
            <Share2 className="h-5 w-5" />
          </button>
          <button 
            className="sm:hidden p-2 hover:bg-gray-100 rounded-full"
            onClick={toggleSidebar}
          >
            <Image className="h-5 w-5" />
          </button>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex flex-1 overflow-hidden relative">
        {/* Chat Section */}
        <div className={`flex-1 flex flex-col ${activeTab === 'chat' ? 'block' : 'hidden sm:block'}`}>
          {/* Fixed height chat container with scrollable content */}
          <div 
            ref={chatContainerRef}
            className="flex-1 overflow-y-auto p-4 space-y-4 max-h-[calc(100vh-250px)] min-h-[200px]"
          >
            {chatHistory.map((message) => (
              <div key={message.id}>
                <div 
                  className={`max-w-2xl mx-auto ${
                    message.type === 'user' ? 'text-right' : 'text-left'
                  }`}
                >
                  <div 
                    className={`inline-block p-3 rounded-lg ${
                      message.type === 'user' 
                        ? 'bg-green-100 text-green-800' 
                        : 'bg-gray-100 text-gray-800'
                    }`}
                  >
                    {message.content}
                  </div>
                </div>
                {message.type === 'system' && message.responseData?.query_results && (
                  <div className="mt-4">
                    {message.responseData.query_results.length === 1 ? (
                      // Single data point - display as text
                      <div className="flex items-center justify-center">
                        <div className="text-center">
                          <h3 className="text-lg font-semibold">{message.responseData.query_results[0][0]}</h3>
                          <p className="text-3xl font-bold text-green-600">{message.responseData.query_results[0][1]}</p>
                        </div>
                      </div>
                    ) : (
                      // Multiple data points - show visualization
                      <DataVisualization
                        data={message.responseData.query_results} 
                      />
                    )}
                  </div>
                )}
              </div>
            ))}
            {isLoading && (
              <div className="text-center text-gray-500">
                Loading...
              </div>
            )}
          </div>

          {/* Chat Input - Fixed at bottom */}
          <form onSubmit={handleSubmit} className="border-t p-4">
            <div className="flex items-center space-x-2">
              <button type="button" className="p-2 hover:bg-gray-100 rounded-full">
                <Camera className="h-5 w-5" />
              </button>
              <button type="button" className="p-2 hover:bg-gray-100 rounded-full">
                <Video className="h-5 w-5" />
              </button>
              <button type="button" className="p-2 hover:bg-gray-100 rounded-full">
                <Paperclip className="h-5 w-5" />
              </button>
              <input 
                type="text"
                value={userInput}
                onChange={(e) => setUserInput(e.target.value)}
                placeholder="Ask Journey anything..."
                className="flex-1 border rounded-full px-4 py-2"
              />
              <button 
                type="submit" 
                disabled={!userInput.trim()}
                className="bg-green-500 text-white px-4 py-2 rounded-full disabled:opacity-50"
              >
                Send
              </button>
            </div>
          </form>
        </div>

        {/* Visualization/Media Section */}
        <div className={`absolute sm:relative w-full sm:w-64 border-l bg-white h-full transition-transform duration-300 ${
          isSidebarOpen ? 'translate-x-0' : 'translate-x-full sm:translate-x-0'
        } right-0 p-4 ${activeTab === 'book' ? 'block' : 'hidden sm:block'}`}>
          <div className="flex h-full flex-col">
            <div className="mb-4 flex justify-between">
              <h2 className="font-semibold">Visualization</h2>
              <button className="p-2 hover:bg-gray-100 rounded-full">
                <MoreVertical className="h-4 w-4" />
              </button>
            </div>
            <div className="flex-1 overflow-auto space-y-4">
              <div className="flex items-center justify-center h-full">
                <div className="text-center">
                  <Mountain className="mx-auto mb-2 h-10 w-10 sm:h-12 sm:w-12 text-gray-400" />
                  <p className="text-sm text-gray-500">No data available for visualization</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default JourneyUI;