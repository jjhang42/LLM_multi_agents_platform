import { useState } from 'react';
import axios from '../utils/api';
import StatusLog from '../components/StatusLog';

// ✅ API Gateway의 응답 형식을 타입으로 명시
interface GatewayResponse {
  result: string;
}

export default function Home() {
  const [input, setInput] = useState('');
  const [logs, setLogs] = useState<string[]>([]);
  const [result, setResult] = useState<string>('');

  const handleSubmit = async () => {
    setLogs(['💬 User Input', '🔄 Sending to API Gateway...']);
    try {
      // ✅ 타입 명시된 axios 요청
      const res = await axios.post<GatewayResponse>('/', { message: input });
      console.log("[DEBUG] Response data:", res.data);
      setLogs(prev => [...prev, '✅ Response Received']);
      setResult(JSON.stringify(res.data.result, null, 2));
    } catch (error) {
      console.error(error);
      setLogs(prev => [...prev, '❌ Error Occurred']);
    }
  };

  return (
    <main className="bg-gray-900 text-white min-h-screen p-6 font-mono">
      <div className="max-w-3xl mx-auto">
        <h1 className="text-2xl font-bold mb-4">LLM Agent Monitoring</h1>
        <textarea
          className="w-full p-3 mb-4 bg-gray-800 text-white border border-gray-700 rounded resize-none"
          rows={4}
          placeholder="Enter your natural language command..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
        />
        <button
          onClick={handleSubmit}
          className="bg-blue-600 hover:bg-blue-500 px-4 py-2 rounded text-white font-semibold"
        >
          Execute
        </button>
        <StatusLog logs={logs} />
        <pre className="bg-gray-800 p-4 mt-4 rounded text-green-400 whitespace-pre-wrap">
          {result}
        </pre>
      </div>
    </main>
  );
}
