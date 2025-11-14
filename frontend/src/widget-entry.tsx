import React from 'react';
import ReactDOM from 'react-dom/client';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import ChatWidget from './components/ChatWidget';
import './index.css';

interface ChatbotWidgetConfig {
  botId: string;
  botName?: string;
  apiBaseUrl?: string;
  primaryColor?: string;
  position?: 'bottom-right' | 'bottom-left';
}

// QueryClient global para el widget
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

// Objeto global ChatbotWidget
const ChatbotWidget = {
  init(config: ChatbotWidgetConfig) {
    const rootElement = document.getElementById('chatbot-widget-root');

    if (!rootElement) {
      console.error('ChatbotWidget Error: No se encontró el elemento #chatbot-widget-root');
      return;
    }

    const root = ReactDOM.createRoot(rootElement);

    root.render(
      <React.StrictMode>
        <QueryClientProvider client={queryClient}>
          <ChatWidget
            botId={config.botId}
            botName={config.botName}
            apiBaseUrl={config.apiBaseUrl}
            primaryColor={config.primaryColor}
            position={config.position}
          />
        </QueryClientProvider>
      </React.StrictMode>
    );
  },
};

// Exportar al objeto global window
declare global {
  interface Window {
    ChatbotWidget: typeof ChatbotWidget;
  }
}

window.ChatbotWidget = ChatbotWidget;

export default ChatbotWidget;
