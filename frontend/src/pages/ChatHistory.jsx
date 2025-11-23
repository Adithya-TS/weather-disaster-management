import { useState, useEffect } from 'react';
import { apiService } from '../services/api';
import { useAuth } from '../context/AuthContext';
import Loader from '../components/ui/Loader';
import toast from 'react-hot-toast';

const ChatHistory = () => {
  const [chats, setChats] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedChat, setSelectedChat] = useState(null);
  const { isAuthenticated } = useAuth();

  useEffect(() => {
    if (isAuthenticated()) {
      fetchChatHistory();
    }
  }, [isAuthenticated]);

  const fetchChatHistory = async () => {
    setLoading(true);
    try {
      const response = await apiService.getChatHistory(50, 0);
      if (response.data.success) {
        setChats(response.data.chats || []);
      }
    } catch (error) {
      console.error('Failed to fetch chat history:', error);
      toast.error('Failed to load chat history');
    } finally {
      setLoading(false);
    }
  };

  const handleChatClick = async (chatId) => {
    try {
      const response = await apiService.getChatById(chatId);
      setSelectedChat(response.data);
    } catch (error) {
      console.error('Failed to fetch chat:', error);
      toast.error('Failed to load chat details');
    }
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleString();
  };

  if (loading) {
    return <Loader fullScreen message="Loading chat history..." />;
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-6 text-gray-900 dark:text-white">
        Chat History
      </h1>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Chat List */}
        <div className="lg:col-span-1">
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4">
            <h2 className="text-xl font-semibold mb-4 text-gray-900 dark:text-white">
              Recent Chats ({chats.length})
            </h2>
            {chats.length === 0 ? (
              <p className="text-gray-500 dark:text-gray-400">No chat history yet</p>
            ) : (
              <div className="space-y-2 max-h-[600px] overflow-y-auto">
                {chats.map((chat) => (
                  <div
                    key={chat.id}
                    onClick={() => handleChatClick(chat.id)}
                    className={`p-3 rounded cursor-pointer transition-colors ${
                      selectedChat?.id === chat.id
                        ? 'bg-blue-100 dark:bg-blue-900'
                        : 'bg-gray-50 dark:bg-gray-700 hover:bg-gray-100 dark:hover:bg-gray-600'
                    }`}
                  >
                    <p className="text-sm font-medium text-gray-900 dark:text-white truncate">
                      {chat.input_text.substring(0, 50)}...
                    </p>
                    <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                      {formatDate(chat.created_at)}
                    </p>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Chat Details */}
        <div className="lg:col-span-2">
          {selectedChat ? (
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
              <div className="mb-4">
                <p className="text-sm text-gray-500 dark:text-gray-400">
                  {formatDate(selectedChat.created_at)}
                </p>
                {selectedChat.model && (
                  <p className="text-sm text-gray-500 dark:text-gray-400">
                    Model: {selectedChat.model}
                  </p>
                )}
              </div>

              <div className="mb-6">
                <h3 className="text-lg font-semibold mb-2 text-gray-900 dark:text-white">
                  Input
                </h3>
                <div className="bg-gray-50 dark:bg-gray-700 p-4 rounded">
                  <p className="text-gray-900 dark:text-white whitespace-pre-wrap">
                    {selectedChat.input_text}
                  </p>
                </div>
              </div>

              <div>
                <h3 className="text-lg font-semibold mb-2 text-gray-900 dark:text-white">
                  Response
                </h3>
                <div className="bg-blue-50 dark:bg-blue-900 p-4 rounded">
                  <p className="text-gray-900 dark:text-white whitespace-pre-wrap">
                    {selectedChat.output_text}
                  </p>
                </div>
              </div>
            </div>
          ) : (
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
              <p className="text-gray-500 dark:text-gray-400 text-center">
                Select a chat from the list to view details
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ChatHistory;

