import { useChat } from './hooks/useChat';
import { formatPrice } from './utils/formatters';

function App() {
  const { messages } = useChat();
  
  console.log('Chat initialized!');
  console.log('Price test:', formatPrice(4999));
  
  return <div>SmartByte Ready!</div>;
}

export default App;